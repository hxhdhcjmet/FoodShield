from flask import Flask, request, jsonify
from project.database.db import init_db, execute, query_one
from project.crypto.pid import generate_pid

import uuid


app = Flask(__name__)


@app.route("/")
def home():
    return """
    <h1>FoodShield Server Running</h1>
    <p>Available test routes:</p>
    <ul>
        <li><a href="/get_order?order_id=123">GET /get_order?order_id=123</a></li>
    </ul>
    <p>POST routes:</p>
    <ul>
        <li>/register</li>
        <li>/create_order</li>
    </ul>
    """


from project.database.db import query_one

@app.route("/register", methods=["POST"])
def register():
    data = request.json

    if not data or "username" not in data:
        return jsonify({"error": "username is required"}), 400

    username = data["username"]

    existing = query_one(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    if existing:
        return jsonify({"error": "username already exists"}), 400

    temp_pid = f"temp_{uuid.uuid4()}"

    try:
        # 先插入用户，拿到 user_id
        user_id = execute(
            "INSERT INTO users (username, pid) VALUES (?, ?)",
            (username, temp_pid)
        )

        # generate_pid 返回的是 dict，不是字符串
        pid_result = generate_pid("FoodShield", str(user_id))
        pid = pid_result["pid"]
        r = pid_result["r"]

        # 如果你的 users 表里还没有 pid_r 字段，就先只更新 pid
        execute(
            "UPDATE users SET pid=? WHERE id=?",
            (pid, user_id)
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "msg": "register success",
        "user_id": user_id,
        "username": username,
        "pid": pid,
        "r": r
    })



@app.route("/create_order", methods=["POST"])
@app.route("/create_order", methods=["POST"])
def create_order():
    data = request.json

    if not data or "user_id" not in data:
        return jsonify({"error": "user_id is required"}), 400

    user_id = data["user_id"]

    user = query_one(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )

    if not user:
        return jsonify({"error": "user not found"}), 404

    order_id = str(uuid.uuid4())

    try:
        execute(
            "INSERT INTO orders (order_id, user_id, token, status) VALUES (?, ?, ?, ?)",
            (order_id, user_id, "temp_token", "created")
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "msg": "order created",
        "order_id": order_id,
        "user_id": user_id,
        "token": "temp_token",
        "status": "created"
    })


@app.route("/get_order", methods=["GET"])
def get_order():
    order_id = request.args.get("order_id")

    return jsonify({
        "order_id": order_id,
        "status": "valid"
    })


if __name__ == "__main__":
    init_db()
    app.run(debug=True)