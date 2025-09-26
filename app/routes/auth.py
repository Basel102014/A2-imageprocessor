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
    user = token.get("userinfo")
    print("[DEBUG] Token:", token)
    print("[DEBUG] User info:", user)
    session["user"] = user
    session["user"]["role"] = "admin" if user.get("cognito:username") == "admin1" else "user"
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
