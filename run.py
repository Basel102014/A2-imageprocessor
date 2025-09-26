from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Cognito Config ---
COGNITO_DOMAIN = "https://ap-southeast-2og65686wi.auth.ap-southeast-2.amazoncognito.com"
COGNITO_USER_POOL_ID = "ap-southeast-2_Og65686Wi"
COGNITO_CLIENT_ID = "60ueg8ts3d58d4vdod86vc95rl"
COGNITO_CLIENT_SECRET = "3gtqge8jb0av1pv8161onf92s5prc5th7u43ad63ltne5014jno"
COGNITO_REDIRECT_URI = "http://localhost:8080/authorize"

# --- OAuth setup ---
oauth = OAuth(app)
oauth.register(
    name="oidc",
    client_id=COGNITO_CLIENT_ID,
    client_secret=COGNITO_CLIENT_SECRET,
    server_metadata_url=f"https://cognito-idp.ap-southeast-2.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile email"},
)

# --- Routes ---
@app.route("/")
def index():
    user = session.get("user")
    if user:
        return f"✅ Logged in as {user['email']}"
    return "❌ Not logged in. <a href='/login'>Login</a>"

@app.route("/login")
def login():
    return oauth.oidc.authorize_redirect(COGNITO_REDIRECT_URI)

@app.route("/authorize")
def authorize():
    token = oauth.oidc.authorize_access_token()
    user = token.get("userinfo")
    print("[DEBUG] Token:", token)
    print("[DEBUG] User info:", user)
    session["user"] = user
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return "✅ Logged out. <a href='/'>Back to home</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
