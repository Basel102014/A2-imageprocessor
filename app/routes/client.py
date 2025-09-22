from flask import Blueprint, render_template, redirect, url_for, request
import jwt
from flask import current_app

client_bp = Blueprint("client", __name__)

@client_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@client_bp.route("/", methods=["GET"])
def root_redirect():
    # Always send root to login
    return redirect(url_for("client.login_page"))

@client_bp.route("/dashboard", methods=["GET"])
def dashboard():
    # Check for token in query params (from JS redirect)
    token = request.args.get("token")
    if not token:
        return redirect(url_for("client.login_page"))

    try:
        jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
    except Exception:
        return redirect(url_for("client.login_page"))

    # If token is valid → show dashboard
    return render_template("index.html")
