from flask import Flask, jsonify
from app.routes.process import process_bp  # Handles actual image work

print("[DEBUG] Starting worker service...")

# --- Flask Setup ---
app = Flask(__name__)
app.register_blueprint(process_bp, url_prefix="/process")

# --- Health Check ---
@app.route("/")
def health():
    return jsonify({"status": "worker service running"}), 200


if __name__ == "__main__":
    print("[DEBUG] Worker service listening on port 5000")
    app.run(host="0.0.0.0", port=5000)
