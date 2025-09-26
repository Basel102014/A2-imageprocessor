from flask import Blueprint, redirect, url_for, session, current_app, request

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
def login():
    """Start Cognito login flow"""
    # Dynamically build the redirect URI from the current host
    redirect_uri = f"{request.scheme}://{request.host}/auth/authorize"
    print(f"[DEBUG] Using redirect URI: {redirect_uri}")
    return current_app.oauth.oidc.authorize_redirect(redirect_uri)


@auth_bp.route("/authorize")
def authorize():
    """Handle callback from Cognito"""
    token = current_app.oauth.oidc.authorize_access_token()
    user = token.get("userinfo")
    print("[DEBUG] Token:", token)
    print("[DEBUG] User info:", user)
    session["user"] = user
    return redirect(url_for("client.dashboard"))


@auth_bp.route("/logout")
def logout():
    """Clear session + logout"""
    session.clear()
    return redirect(url_for("auth.index"))


@auth_bp.route("/")
def index():
    user = session.get("user")
    if user:
        return f"✅ Logged in as {user['email']} <a href='/auth/logout'>Logout</a>"
    return "❌ Not logged in. <a href='/auth/login'>Login</a>"