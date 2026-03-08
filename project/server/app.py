from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "FoodShield Server Running"


from flask import Flask, request, jsonify

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


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")

    return jsonify({
        "msg": "register success",
        "username": username
    })


@app.route("/create_order", methods=["POST"])
def create_order():
    data = request.json
    order_id = data.get("order_id")

    return jsonify({
        "msg": "order created",
        "order_id": order_id
    })


@app.route("/get_order", methods=["GET"])
def get_order():
    order_id = request.args.get("order_id")

    return jsonify({
        "order_id": order_id,
        "status": "valid"
    })


if __name__ == "__main__":
    app.run(debug=True)


@app.route("/create_order", methods=["POST"])
def create_order():
    data = request.json
    order_id = data.get("order_id")

    return jsonify({
        "msg": "order created",
        "order_id": order_id
    })

@app.route("/get_order", methods=["GET"])
def get_order():
    order_id = request.args.get("order_id")

    return jsonify({
        "order_id": order_id,
        "status": "valid"
    })


if __name__ == "__main__":
    app.run(debug=True)
