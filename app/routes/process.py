import time
from flask import Blueprint, request, jsonify, current_app, g
from PIL import Image, ImageFilter
import os
from app.utils.auth import token_required, admin_required
from app.utils.data_store import save_metadata

process_bp = Blueprint("process", __name__)

@process_bp.route("/", methods=["POST"])
@token_required
def process_image():
    """
    Normal image processing endpoint.
    Applies a small number of transformations and saves result.
    Good for demoing functionality without CPU overload.
    """
    filename = request.json.get("filename")
    if not filename:
        return jsonify({"error": "Filename required"}), 400

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    result_folder = current_app.config["RESULT_FOLDER"]

    input_path = os.path.join(upload_folder, filename)
    if not os.path.exists(input_path):
        return jsonify({"error": "File not found"}), 404

    os.makedirs(result_folder, exist_ok=True)

    img = Image.open(input_path)

    # Apply just a few operations
    processed = img.filter(ImageFilter.GaussianBlur(radius=5))
    processed = processed.rotate(-90)

    out_name = f"processed_{filename}"
    out_path = os.path.join(result_folder, out_name)
    processed.save(out_path)


    record = save_metadata(filename, out_name, g.user)
    return jsonify({
        "message": f"Processed {filename}",
        "result": out_name,
        "metadata": record
    }), 200

@process_bp.route("/stress", methods=["POST"])
@admin_required
def stress_test():
    """
    Dedicated endpoint for CPU load testing.
    Runs heavy image processing for a set duration.
    """
    filename = request.json.get("filename")
    duration = int(request.json.get("duration", 300))  # default 5 minutes

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    input_path = os.path.join(upload_folder, filename)

    if not os.path.exists(input_path):
        return jsonify({"error": "File not found"}), 404

    img = Image.open(input_path)
    start_time = time.time()
    counter = 0

    while time.time() - start_time < duration:
        # CPU-heavy but skip saving each time
        processed = img.filter(ImageFilter.GaussianBlur(radius=10))
        processed = processed.rotate(90)
        counter += 1

    # Save just one final result
    result_folder = current_app.config["RESULT_FOLDER"]
    os.makedirs(result_folder, exist_ok=True)
    out_name = f"stress_{filename}"
    out_path = os.path.join(result_folder, out_name)
    processed.save(out_path)

    record = save_metadata(filename, out_name, g.user)
    return jsonify({
        "message": f"Processed {filename}",
        "result": out_name,
        "metadata": record
    }), 200
