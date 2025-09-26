from urllib.parse import urlencode
from flask import Blueprint, redirect, render_template, url_for, session, current_app, request
import os

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
def login():
    if os.environ.get("FLASK_ENV") == "production":
        redirect_uri = "https://n11326158.cab432.com/auth/authorize"
    else:
        redirect_uri = f"{request.scheme}://{request.host}/auth/authorize"

    print(f"[DEBUG] Using redirect URI: {redirect_uri}")
    return current_app.oauth.oidc.authorize_redirect(
        redirect_uri,
        prompt="login"
    )

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
    session.clear()

    # Hosted UI base
    authz = current_app.oauth.oidc.server_metadata.get("authorization_endpoint")
    hosted_base = authz.split("/oauth2/authorize")[0] if authz else \
        "https://ap-southeast-2og65686wi.auth.ap-southeast-2.amazoncognito.com"

    client_id = getattr(current_app.oauth.oidc, "client_id", None)

    if os.environ.get("FLASK_ENV") == "production":
        post_logout = "https://n11326158.cab432.com/auth/"
    else:
        post_logout = f"{request.scheme}://{request.host}/auth/"

    params = {"client_id": client_id, "logout_uri": post_logout}
    logout_url = f"{hosted_base}/logout?{urlencode(params)}"

    print("[DEBUG] Cognito logout URL:", logout_url)
    return redirect(logout_url)

@auth_bp.route("/")
def index():
    """Show a simple login page"""
    return """
    <html>
      <head><title>Login</title></head>
      <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
        <h2>Welcome</h2>
        <a href='/auth/login'>
          <button style="padding: 10px 20px; font-size: 16px;">Login with Cognito</button>
        </a>
      </body>
    </html>
    """
