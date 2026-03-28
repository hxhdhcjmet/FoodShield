from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
from pathlib import Path
from datetime import datetime
import uuid
from project.crypto.message_utils import calculate_message_hash

from project.database.db import init_db, execute, query_one, query_all
from project.crypto.pid import generate_pid
from project.crypto.token_utils import generate_token, verify_token

app = Flask(__name__)
app.config["SECRET_KEY"] = "foodshield-secret-key"

CORS(app)
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
    manage_session=False,
    logger=True,
    engineio_logger=True
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "project" / "frontend"


# ====================== 工具函数 ======================

def now_iso():
    return datetime.now().isoformat(timespec="seconds")

def get_order_by_order_id(order_id: str):
    return query_one("SELECT * FROM orders WHERE order_id = ?", (order_id,))


def save_message(msg_id, order_id, sender_pid, role, content, message_hash, timestamp):
    execute(
        """
        INSERT INTO messages (msg_id, order_id, sender_pid, role, content, message_hash, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (msg_id, order_id, sender_pid, role, content, message_hash, timestamp)
    )


def get_message_history_by_order(order_id: str):
    rows = query_all(
        """
        SELECT msg_id, order_id, sender_pid, role, content, message_hash, timestamp
        FROM messages
        WHERE order_id = ?
        ORDER BY id ASC
        """,
        (order_id,)
    )
    return [dict(row) for row in rows]


# ====================== 前端页面路由 ======================

@app.route("/")
def index_page():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/index.html")
def index_html():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/user.html")
def user_page():
    return send_from_directory(FRONTEND_DIR, "user.html")


@app.route("/rider.html")
def rider_page():
    return send_from_directory(FRONTEND_DIR, "rider.html")


@app.route("/admin.html")
def admin_page():
    return send_from_directory(FRONTEND_DIR, "admin.html")


@app.route("/css/<path:filename>")
def css_files(filename):
    return send_from_directory(FRONTEND_DIR / "css", filename)


# ====================== 后端业务 API ======================

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if not data or "username" not in data:
        return jsonify({"success": False, "message": "username is required"}), 400

    username = data["username"].strip()
    if not username:
        return jsonify({"success": False, "message": "username cannot be empty"}), 400

    existing = query_one("SELECT * FROM users WHERE username = ?", (username,))
    if existing:
        return jsonify({"success": False, "message": "username already exists"}), 400

    try:
        # 先插入临时 PID
        temp_pid = f"temp_{uuid.uuid4()}"
        user_id = execute(
            "INSERT INTO users (username, pid) VALUES (?, ?)",
            (username, temp_pid)
        )

        # 生成真实 PID
        pid_result = generate_pid("FoodShield", str(user_id))
        pid = pid_result["pid"]

        execute("UPDATE users SET pid = ? WHERE id = ?", (pid, user_id))

        return jsonify({
            "success": True,
            "message": "user registered successfully",
            "data": {
                "user_id": user_id,
                "username": username,
                "pid": pid
            }
        }), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/create_order", methods=["POST"])
def create_order():
    data = request.json
    if not data or "pid" not in data:
        return jsonify({"success": False, "message": "pid is required"}), 400

    pid = data["pid"]

    user = query_one("SELECT * FROM users WHERE pid = ?", (pid,))
    if not user:
        return jsonify({"success": False, "message": "user not found"}), 404

    user_id = user["id"]
    order_id = str(uuid.uuid4())

    token_data = generate_token(order_id, pid)
    token = token_data["token"]
    timestamp = token_data["timestamp"]

    try:
        execute(
            """
            INSERT INTO orders (order_id, user_id, token, token_timestamp, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (order_id, user_id, token, timestamp, "created")
        )

        return jsonify({
            "success": True,
            "message": "order created successfully",
            "data": {
                "order_id": order_id,
                "pid": pid,
                "token": token,
                "timestamp": timestamp,
                "status": "created"
            }
        }), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/verify_order", methods=["POST"])
def verify_order_api():
    data = request.json
    required = ["order_id", "pid", "timestamp", "token"]

    for field in required:
        if not data or field not in data:
            return jsonify({"success": False, "message": f"{field} is required"}), 400

    is_valid = verify_token(
        data["order_id"],
        data["pid"],
        data["timestamp"],
        data["token"]
    )

    return jsonify({
        "success": True,
        "message": "order verification completed",
        "data": {
            "valid": is_valid
        }
    }), 200


@app.route("/get_pending_orders", methods=["GET"])
def get_pending_orders():
    try:
        rows = query_all(
            """
            SELECT o.order_id, o.status, u.pid
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.status = 'created'
            ORDER BY o.id DESC
            """
        )

        orders = []
        for row in rows:
            orders.append({
                "order_id": row["order_id"],
                "status": row["status"],
                "pid": row["pid"]
            })

        return jsonify({
            "success": True,
            "message": "pending orders fetched successfully",
            "data": orders
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/take_order", methods=["POST"])
def take_order():
    data = request.json
    if not data or "order_id" not in data:
        return jsonify({"success": False, "message": "order_id is required"}), 400

    order_id = data["order_id"]

    try:
        order = get_order_by_order_id(order_id)
        if not order:
            return jsonify({"success": False, "message": "order not found"}), 404

        if order["status"] != "created":
            return jsonify({
                "success": False,
                "message": f"order cannot be taken, current status: {order['status']}"
            }), 400

        execute(
            "UPDATE orders SET status = ? WHERE order_id = ?",
            ("taken", order_id)
        )

        return jsonify({
            "success": True,
            "message": "order taken successfully",
            "data": {
                "order_id": order_id,
                "status": "taken"
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/get_message_history/<order_id>", methods=["GET"])
def get_message_history(order_id):
    try:
        order = get_order_by_order_id(order_id)
        if not order:
            return jsonify({"success": False, "message": "order not found"}), 404

        history = get_message_history_by_order(order_id)
        return jsonify({
            "success": True,
            "message": "message history fetched successfully",
            "data": history
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ====================== WebSocket 事件 ======================

@socketio.on("connect")
def handle_connect():
    emit("system_message", {
        "type": "system",
        "message": "websocket connected",
        "timestamp": now_iso()
    })


@socketio.on("join_order")
def handle_join_order(data):
    """
    用户侧进入订单聊天房间
    data = {
        "order_id": "...",
        "pid": "...",
        "timestamp": "...",
        "token": "...",
        "role": "user"
    }
    """
    print("=== join_order received ===")
    print("raw data:", data)

    required = ["order_id", "pid", "timestamp", "token", "role"]
    for field in required:
        if not data or field not in data:
            print(f"join_order failed: missing field -> {field}")
            emit("join_result", {
                "success": False,
                "message": f"{field} is required"
            })
            return

    order_id = data["order_id"]
    pid = data["pid"]
    timestamp = data["timestamp"]
    token = data["token"]
    role = data["role"]

    print("order_id =", order_id)
    print("pid =", pid)
    print("timestamp =", timestamp)
    print("role =", role)
    print("token prefix =", token[:16] + "..." if token else "")

    order = get_order_by_order_id(order_id)
    print("order found =", bool(order))

    if not order:
        print("join_order failed: order not found")
        emit("join_result", {
            "success": False,
            "message": "order not found"
        })
        return

    is_valid = verify_token(order_id, pid, timestamp, token)
    print("verify_token result =", is_valid)

    if not is_valid:
        print("join_order failed: order verification failed")
        emit("join_result", {
            "success": False,
            "message": "order verification failed"
        })
        return

    join_room(order_id)
    print("join_order success: joined room", order_id)

    emit("join_result", {
        "success": True,
        "message": f"{role} joined room successfully",
        "order_id": order_id
    })

    emit("system_message", {
        "type": "system",
        "order_id": order_id,
        "message": f"{role} entered the chat room",
        "timestamp": now_iso()
    }, room=order_id)


@socketio.on("join_order_as_rider")
def handle_join_order_as_rider(data):
    """
    骑手侧进入订单聊天房间
    data = {
        "order_id": "...",
        "role": "rider"
    }
    """
    required = ["order_id", "role"]
    for field in required:
        if not data or field not in data:
            emit("join_result", {
                "success": False,
                "message": f"{field} is required"
            })
            return

    order_id = data["order_id"]
    role = data["role"]

    order = get_order_by_order_id(order_id)
    if not order:
        emit("join_result", {
            "success": False,
            "message": "order not found"
        })
        return

    if order["status"] not in ("taken", "delivering", "completed"):
        emit("join_result", {
            "success": False,
            "message": f"rider cannot join, current order status: {order['status']}"
        })
        return

    join_room(order_id)

    emit("join_result", {
        "success": True,
        "message": f"{role} joined room successfully",
        "order_id": order_id
    })

    emit("system_message", {
        "type": "system",
        "order_id": order_id,
        "message": f"{role} entered the chat room",
        "timestamp": now_iso()
    }, room=order_id)


@socketio.on("send_message")
def handle_send_message(data):
    """
    data = {
        "order_id": "...",
        "sender_pid": "...",
        "role": "user" / "rider",
        "content": "..."
    }
    """
    required = ["order_id", "sender_pid", "role", "content"]
    for field in required:
        if not data or field not in data:
            emit("error_message", {
                "type": "error",
                "message": f"{field} is required"
            })
            return

    order_id = data["order_id"]
    sender_pid = data["sender_pid"]
    role = data["role"]
    content = str(data["content"]).strip()

    if not content:
        emit("error_message", {
            "type": "error",
            "message": "content cannot be empty"
        })
        return

    order = get_order_by_order_id(order_id)
    if not order:
        emit("error_message", {
            "type": "error",
            "message": "order not found"
        })
        return

    timestamp = now_iso()
    message_hash = calculate_message_hash(
        order_id,
        sender_pid,
        role,
        content,
        timestamp
    )

    msg = {
    "type": "chat",
    "msg_id": str(uuid.uuid4()),
    "order_id": order_id,
    "sender_pid": sender_pid,
    "role": role,
    "content": content,
    "message_hash": message_hash,
    "timestamp": timestamp
    }

    try:
        save_message(
            msg["msg_id"],
            msg["order_id"],
            msg["sender_pid"],
            msg["role"],
            msg["content"],
            msg["message_hash"],
            msg["timestamp"]
        )

        emit("receive_message", msg, room=order_id)

    except Exception as e:
        emit("error_message", {
            "type": "error",
            "message": str(e)
        })


# ====================== 启动 ======================

if __name__ == "__main__":
    init_db()
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)