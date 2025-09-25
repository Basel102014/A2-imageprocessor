from flask import Blueprint, request, jsonify
from app.services.jwt_handler import encode_jwt

auth_bp = Blueprint("auth", __name__)

USERS = {
    "admin": {"password": "admin", "role": "admin"},
    "bailey": {"password": "qut", "role": "user"}
}

@auth_bp.route("/login", methods=["POST"])
def login():
    print("[DEBUG] /login route hit")  # Entry point
    data = request.get_json()
    print(f"[DEBUG] Incoming data: {data}")

    username = data.get("username")
    password = data.get("password")
    print(f"[DEBUG] Username: {username}, Password: {password}")

    if username in USERS:
        print(f"[DEBUG] Found user '{username}' in USERS")
        if USERS[username]["password"] == password:
            print("[DEBUG] Password match successful")
            role = USERS[username]["role"]
            print(f"[DEBUG] Role: {role}")
            token = encode_jwt(username, role)
            print(f"[DEBUG] Generated JWT: {token}")
            return jsonify({"token": token})
        else:
            print("[DEBUG] Password mismatch")
    else:
        print(f"[DEBUG] Username '{username}' not found in USERS")

    print("[DEBUG] Returning 401 Invalid credentials")
    return jsonify({"error": "Invalid credentials"}), 401
