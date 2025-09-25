from functools import wraps
from flask import request, jsonify, current_app, g
import jwt


def token_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            print(f"[DEBUG] token_required wrapper triggered for function '{f.__name__}' (role required={role})")
            token = None

            # Extract token from header
            auth_header = request.headers.get("Authorization")
            print(f"[DEBUG] Authorization header: {auth_header}")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                print(f"[DEBUG] Extracted token: {token[:30]}... (truncated)")
            else:
                print("[DEBUG] No Bearer token in Authorization header")

            if not token:
                print("[DEBUG] Token missing → 401")
                return jsonify({"error": "Token missing"}), 401

            try:
                # Decode JWT
                payload = jwt.decode(
                    token,
                    current_app.config["JWT_SECRET"],
                    algorithms=["HS256"]
                )
                print(f"[DEBUG] Decoded JWT payload: {payload}")

                # Store full payload so g.user is always a dict
                g.user = {
                    "username": payload.get("user"),
                    "role": payload.get("role")
                }
                g.role = g.user["role"]
                print(f"[DEBUG] g.user set → {g.user}")

                # Role check
                if role and g.role != role:
                    print(f"[DEBUG] Role mismatch: required={role}, got={g.role} → 403")
                    return jsonify({"error": f"{role.capitalize()} access required"}), 403

            except Exception as e:
                print(f"[DEBUG] JWT decode failed: {e}")
                return jsonify({"error": "Token invalid", "details": str(e)}), 401

            print(f"[DEBUG] Access granted for user '{g.user['username']}' with role '{g.role}'")
            return f(*args, **kwargs)
        return decorated
    return decorator
