from flask import Blueprint, redirect, url_for, session, current_app, request

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
def login():
    """Start Cognito login flow immediately"""
    redirect_uri = f"{request.scheme}://{request.host}/auth/authorize"
    print(f"[DEBUG] Using redirect URI: {redirect_uri}")
    return current_app.oauth.oidc.authorize_redirect(redirect_uri)


@auth_bp.route("/authorize")
def authorize():
    """Handle callback from Cognito"""
    token = current_app.oauth.oidc.authorize_access_token()
    user = token.get("userinfo") or {}

    # Also decode the ID token to extract Cognito groups
    import base64, json
    def _decode_jwt(jwt):
        try:
            payload = jwt.split(".")[1]
            payload += "=" * (-len(payload) % 4)  # fix padding
            return json.loads(base64.urlsafe_b64decode(payload.encode()).decode())
        except Exception:
            return {}

    id_token = token.get("id_token")
    claims = _decode_jwt(id_token) if id_token else {}

    groups = claims.get("cognito:groups", [])
    role = "admin" if any(g.lower() == "admin" for g in groups) else "user"

    username = (
        user.get("cognito:username")
        or user.get("preferred_username")
        or user.get("email", "").split("@")[0]
        or "unknown"
    )

    user["username"] = username
    user["role"] = role
    session["user"] = user

    print("[DEBUG] /auth/authorize → user authenticated")
    print("[DEBUG] Groups:", groups)
    print("[DEBUG] Username:", username)
    print("[DEBUG] Role:", role)
    print("[DEBUG] Session user:", session["user"])

    return redirect(url_for("client.dashboard"))



@auth_bp.route("/logout")
def logout():
    """Clear session + logout, then go straight to Cognito login again"""
    session.clear()
    return redirect(url_for("auth.login"))


@auth_bp.route("/")
def index():
    """Shortcut root → always redirect to login flow"""
    return redirect(url_for("auth.login"))
