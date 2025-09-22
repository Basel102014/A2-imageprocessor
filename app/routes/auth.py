from flask import Blueprint, request, jsonify
import jwt, datetime
from app.services.jwt_handler import encode_jwt

auth_bp = Blueprint("auth", __name__)

# Hardcoded users for now
USERS = {"admin": "password1", "guest": "password2"}

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username in USERS and USERS[username] == password:
        token = encode_jwt(username)
        return jsonify({"token": token})
    return jsonify({"error": "Invalid credentials"}), 401