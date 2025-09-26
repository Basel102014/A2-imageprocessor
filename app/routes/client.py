from flask import Blueprint, redirect, render_template, session, url_for
from app.utils.auth_helper import login_required

client_bp = Blueprint("client", __name__)

@client_bp.route("/dashboard")
@login_required
def dashboard():
    user = session.get("user")
    return render_template("index.html", user=user)
