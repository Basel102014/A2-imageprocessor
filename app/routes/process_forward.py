import time
import requests
from flask import Blueprint, request, jsonify, session
from app.utils.auth_helper import login_required

process_forward_bp = Blueprint("process_forward", __name__)

WORKER_URL = "http://internal-n11326158-alb-1562283677.ap-southeast-2.elb.amazonaws.com"


def check_worker_health():
    """Ping the worker's /health endpoint before sending a job."""
    try:
        resp = requests.get(f"{WORKER_URL}/", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "worker service running":
                print("[DEBUG] Worker health check: OK")
                return True
        print(f"[WARN] Worker health check failed: {resp.text}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Worker health check request failed: {e}")
    return False


@process_forward_bp.route("/", methods=["POST"])
@login_required
def process_image():
    """Forward image processing requests to the worker service."""
    data = request.json

    if not check_worker_health():
        return jsonify({"error": "Worker service unavailable"}), 503

    try:
        resp = requests.post(f"{WORKER_URL}/process", json=data, timeout=120)
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to contact worker: {e}")
        return jsonify({"error": "Worker service unreachable"}), 500

@process_forward_bp.route("/stress", methods=["POST"])
@login_required
def stress_test():
    """Send repeated /process requests to stress test worker scaling."""
    print("[DEBUG] /stress route hit (POST)")
    data = request.json
    filename = data.get("filename")
    duration = int(data.get("duration", 30))

    if not filename:
        return jsonify({"error": "Filename required"}), 400

    if not check_worker_health():
        return jsonify({"error": "Worker service unavailable"}), 503

    worker_url = f"{WORKER_URL}/process"
    end_time = time.time() + duration
    sent, successes, failures = 0, 0, 0

    print(f"[INFO] Starting stress test for {duration}s (spamming {worker_url})")

    while time.time() < end_time:
        try:
            # Heavier workload: upscale image 30x and apply minor rotation
            resp = requests.post(worker_url, json={
                "filename": filename,
                "operations": {
                    "rotate": 5,
                    "upscale": 30
                }
            }, timeout=60)

            sent += 1
            if resp.status_code == 200:
                successes += 1
            else:
                failures += 1
                print(f"[WARN] Request failed: {resp.status_code}")

        except Exception as e:
            failures += 1
            print(f"[ERROR] Request error: {e}")

    summary = {
        "duration": duration,
        "requests_sent": sent,
        "successes": successes,
        "failures": failures
    }

    print(f"[INFO] Stress test summary: {summary}")
    return jsonify(summary), 200
