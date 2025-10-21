import requests
from flask import Blueprint, request, jsonify, session
from app.utils.auth_helper import login_required

process_forward_bp = Blueprint("process_forward", __name__)

# Worker EC2 private DNS (internal network)
WORKER_URL = "http://internal-n11326158-alb-1562283677.ap-southeast-2.elb.amazonaws.com"

def check_worker_health():
    """Ping the worker's /health endpoint before sending a job."""
    try:
        health_resp = requests.get(f"{WORKER_URL}/", timeout=5)
        if health_resp.status_code == 200:
            data = health_resp.json()
            if data.get("status") == "worker service running":
                print("[DEBUG] Worker health check: OK")
                return True
        print(f"[WARN] Worker health check failed: {health_resp.text}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Worker health check request failed: {e}")
    return False


@process_forward_bp.route("/", methods=["POST"])
@login_required
def process_image():
    data = request.json

    # Check worker health first
    if not check_worker_health():
        return jsonify({"error": "Worker service unavailable"}), 503

    try:
        response = requests.post(f"{WORKER_URL}/process", json=data, timeout=120)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to contact worker: {e}")
        return jsonify({"error": "Worker service unreachable"}), 500


@process_forward_bp.route("/stress", methods=["POST"])
@login_required
def stress_test():
    data = request.json

    # Check worker health first
    if not check_worker_health():
        return jsonify({"error": "Worker service unavailable"}), 503

    try:
        response = requests.post(f"{WORKER_URL}/process/stress", json=data, timeout=300)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to contact worker for stress test: {e}")
        return jsonify({"error": "Worker service unreachable"}), 500
