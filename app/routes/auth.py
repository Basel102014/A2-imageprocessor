from flask import Blueprint, request, jsonify, current_app
import jwt
import datetime

auth_bp = Blueprint("auth", __name__)

USERS = {
    "alice": {"password": "password123", "role": "admin"},
    "bob": {"password": "qutrocks", "role": "user"}
}

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username in USERS and USERS[username]["password"] == password:
        token = jwt.encode(
            {
                "user": username,
                "role": USERS[username]["role"],   # include role in token
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            },
            current_app.config["JWT_SECRET"],
            algorithm="HS256"
        )
        return jsonify({"token": token})

    return jsonify({"error": "Invalid credentials"}), 401
