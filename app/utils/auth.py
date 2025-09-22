from functools import wraps
from flask import request, jsonify, current_app, g
import jwt

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return jsonify({"error": "Token missing"}), 401

        try:
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET"],
                algorithms=["HS256"]
            )
            g.user = payload.get("user")
            if payload.get("role") != "admin":
                return jsonify({"error": "Admin access required"}), 403
        except Exception as e:
            return jsonify({"error": "Token invalid", "details": str(e)}), 401

        return f(*args, **kwargs)

    return decorated


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return jsonify({"error": "Token missing"}), 401

        try:
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET"],
                algorithms=["HS256"]
            )
            g.user = payload.get("user")
        except Exception as e:
            return jsonify({"error": "Token invalid", "details": str(e)}), 401

        return f(*args, **kwargs)

    return decorated