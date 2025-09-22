from flask import Blueprint, request, jsonify
from app.services.jwt_handler import encode_jwt

auth_bp = Blueprint("auth", __name__)

USERS = {
    "admin": {"password": "admin", "role": "admin"},
    "bailey": {"password": "qut", "role": "user"}
}

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username in USERS and USERS[username]["password"] == password:
        role = USERS[username]["role"]
        token = encode_jwt(username, role)
        return jsonify({"token": token})

    return jsonify({"error": "Invalid credentials"}), 401
