from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
from project.database.db import init_db, execute, query_one
from project.crypto.pid import generate_pid
from project.crypto.token_utils import generate_token, verify_token
import uuid

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "project" / "frontend"


# ===== 前端页面路由 =====
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


# ===== 后端 API =====
@app.route("/register", methods=["POST"])
def register():
    data = request.json

    if not data or "username" not in data:
        return jsonify({
            "success": False,
            "message": "username is required"
        }), 400

    username = data["username"]

    existing = query_one(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    if existing:
        return jsonify({
            "success": False,
            "message": "username already exists"
        }), 400

    temp_pid = f"temp_{uuid.uuid4()}"

    try:
        user_id = execute(
            "INSERT INTO users (username, pid) VALUES (?, ?)",
            (username, temp_pid)
        )

        pid_result = generate_pid("FoodShield", str(user_id))
        pid = pid_result["pid"]
        r = pid_result["r"]

        execute(
            "UPDATE users SET pid=? WHERE id=?",
            (pid, user_id)
        )

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    return jsonify({
        "success": True,
        "message": "user registered successfully",
        "data": {
            "user_id": user_id,
            "username": username,
            "pid": pid,
            "r": r
        }
    }), 201


@app.route("/create_order", methods=["POST"])
def create_order():
    data = request.json

    if not data or "pid" not in data:
        return jsonify({
            "success": False,
            "message": "pid is required"
        }), 400

    pid = data["pid"]

    user = query_one(
        "SELECT * FROM users WHERE pid = ?",
        (pid,)
    )

    if not user:
        return jsonify({
            "success": False,
            "message": "user not found"
        }), 404

    user_id = user["id"]
    order_id = str(uuid.uuid4())

    token_data = generate_token(order_id, pid)
    token = token_data["token"]
    timestamp = token_data["timestamp"]

    try:
        execute(
            "INSERT INTO orders (order_id, user_id, token, token_timestamp, status) VALUES (?, ?, ?, ?, ?)",
            (order_id, user_id, token, timestamp, "created")
        )
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

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


@app.route("/verify_order", methods=["POST"])
def verify_order_api():
    data = request.json

    required_fields = ["order_id", "pid", "timestamp", "token"]
    for field in required_fields:
        if not data or field not in data:
            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

    order_id = data["order_id"]
    pid = data["pid"]
    timestamp = data["timestamp"]
    provided_token = data["token"]

    is_valid = verify_token(order_id, pid, timestamp, provided_token)

    return jsonify({
        "success": True,
        "message": "order verification completed",
        "data": {
            "order_id": order_id,
            "pid": pid,
            "valid": is_valid
        }
    }), 200


if __name__ == "__main__":
    init_db()
    app.run(debug=True)