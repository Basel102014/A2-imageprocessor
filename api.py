from flask import Flask, redirect, url_for
from authlib.integrations.flask_client import OAuth
import os
from app.services.param_store import get_param
from app.services.secrets import get_secret

print("[DEBUG] Starting application…")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "app", "templates"),
    static_folder=os.path.join(BASE_DIR, "app", "static")
)
app.secret_key = os.urandom(24)

# --- Cognito Config ---
COGNITO_USER_POOL_ID = get_param("/n11326158/cognito/COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = get_param("/n11326158/cognito/COGNITO_CLIENT_ID")
COGNITO_CLIENT_SECRET = get_secret()
COGNITO_DOMAIN_URL = get_param("/n11326158/cognito/DOMAIN_URL")

# --- OAuth setup ---
oauth = OAuth(app)
app.oauth = oauth

oauth.register(
    name="oidc",
    client_id=COGNITO_CLIENT_ID,
    client_secret=COGNITO_CLIENT_SECRET,
    server_metadata_url=f"{COGNITO_DOMAIN_URL}/{COGNITO_USER_POOL_ID}/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile email"},
)
print("[DEBUG] Cognito OAuth provider registered")

# --- Root redirect ---
@app.route("/")
def root_redirect():
    print("[DEBUG] Root path hit → redirecting to /auth/")
    return redirect(url_for("auth.index"))

# --- Register blueprints ---
from app.routes.auth import auth_bp
from app.routes.client import client_bp
from app.routes.upload import upload_bp
from app.routes.results import results_bp
from app.routes.process_forward import process_forward_bp  # microservice forwarding

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(client_bp)
app.register_blueprint(upload_bp, url_prefix="/upload")
app.register_blueprint(results_bp, url_prefix="/results")
app.register_blueprint(process_forward_bp, url_prefix="/process")

print("[DEBUG] Registered blueprints: auth, client, upload, results, process_forward")

# --- Health check ---
@app.route("/health")
def health():
    return {"status": "API service running"}, 200

# --- Run app ---
if __name__ == "__main__":
    print("[DEBUG] Running app on host=0.0.0.0, port=8080")
    app.run(host="0.0.0.0", port=8080, debug=True)
