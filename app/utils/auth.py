from functools import wraps
from flask import request, jsonify, current_app, g
import jwt


def token_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None

            # Extract token from header
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

            if not token:
                return jsonify({"error": "Token missing"}), 401

            try:
                # Decode JWT
                payload = jwt.decode(
                    token,
                    current_app.config["JWT_SECRET"],
                    algorithms=["HS256"]
                )

                # Store full payload so g.user is always a dict
                g.user = {
                    "username": payload.get("user"),
                    "role": payload.get("role")
                }
                g.role = g.user["role"]

                # Role check
                if role and g.role != role:
                    return jsonify({"error": f"{role.capitalize()} access required"}), 403

            except Exception as e:
                return jsonify({"error": "Token invalid", "details": str(e)}), 401

            return f(*args, **kwargs)
        return decorated
    return decorator
