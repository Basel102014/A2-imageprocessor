from functools import wraps
from flask import request, jsonify, current_app, g
import jwt

def token_required(role=None):
    def decorator(f):
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
                g.role = payload.get("role")

                if role and g.role != role:
                    return jsonify({"error": f"{role.capitalize()} access required"}), 403

            except Exception as e:
                return jsonify({"error": "Token invalid", "details": str(e)}), 401

            return f(*args, **kwargs)
        return decorated
    return decorator
