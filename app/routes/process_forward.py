import requests
from flask import Blueprint, request, jsonify, session
from app.utils.auth_helper import login_required

process_forward_bp = Blueprint("process_forward", __name__)

# Worker EC2 private DNS
WORKER_URL = "http://ip-172-31-87-146.ap-southeast-2.compute.internal:5000"

@process_forward_bp.route("/", methods=["POST"])
@login_required
def process_image():
    data = request.json
    try:
        response = requests.post(f"{WORKER_URL}/process", json=data,    timeout=120)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to contact worker: {e}")
        return jsonify({"error": "Worker service unreachable"}), 500

@process_forward_bp.route("/stress", methods=["POST"])
@login_required
def stress_test():
    data = request.json
    try:
        response = requests.post(f"{WORKER_URL}/process/stress", json=data, timeout=300)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to contact worker for stress test: {e}")
        return jsonify({"error": "Worker service unreachable"}), 500
