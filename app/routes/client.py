from flask import Blueprint, render_template, redirect, url_for, request
import jwt
from flask import current_app

client_bp = Blueprint("client", __name__)

@client_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@client_bp.route("/", methods=["GET"])
def root_redirect():
    return redirect(url_for("client.login_page"))

@client_bp.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("index.html")