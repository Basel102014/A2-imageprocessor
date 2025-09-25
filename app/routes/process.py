import time
import uuid
from flask import Blueprint, request, jsonify, current_app, g
from PIL import Image, ImageFilter, ImageOps
import os
from app.utils.auth import token_required
from app.utils.data_store import save_results_metadata

process_bp = Blueprint("process", __name__)


def unique_filename(prefix, original_name, result_folder):
    """Generate a unique output filename to avoid overwriting."""
    base, ext = os.path.splitext(original_name)
    while True:
        # Use timestamp + uuid for uniqueness
        candidate = f"{prefix}_{base}_{int(time.time())}_{uuid.uuid4().hex[:6]}{ext}"
        if not os.path.exists(os.path.join(result_folder, candidate)):
            return candidate


@process_bp.route("/", methods=["POST"])
@token_required()
def process_image():
    data = request.json
    filename = data.get("filename")
    operations = data.get("operations", {})

    if not filename:
        return jsonify({"error": "Filename required"}), 400

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    result_folder = current_app.config["RESULT_FOLDER"]

    input_path = os.path.join(upload_folder, filename)
    if not os.path.exists(input_path):
        return jsonify({"error": "File not found"}), 404

    os.makedirs(result_folder, exist_ok=True)

    try:
        img = Image.open(input_path)

        # --- Apply operations ---
        if "rotate" in operations:
            angle = float(operations["rotate"])
            img = img.rotate(angle, expand=True)

        if "blur" in operations:
            radius = float(operations["blur"])
            img = img.filter(ImageFilter.GaussianBlur(radius=radius))

        if "resize" in operations:
            resize_conf = operations["resize"]
            w = int(resize_conf.get("width", img.width))
            h = int(resize_conf.get("height", img.height))
            img = img.resize((w, h))

        if "upscale" in operations:
            factor = float(operations["upscale"])
            w, h = int(img.width * factor), int(img.height * factor)
            img = img.resize((w, h))

        if operations.get("grayscale"):
            img = ImageOps.grayscale(img)

        if "flip" in operations:
            mode = operations["flip"].lower()
            if mode == "horizontal":
                img = ImageOps.mirror(img)
            elif mode == "vertical":
                img = ImageOps.flip(img)

        # --- Save output with unique name ---
        out_name = unique_filename("processed", filename, result_folder)
        out_path = os.path.join(result_folder, out_name)
        img.save(out_path)

        record = save_results_metadata(filename, out_name, g.user)
        return jsonify({
            "message": f"Processed {filename}",
            "result": out_name,
            "metadata": record
        }), 200

    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500


@process_bp.route("/stress", methods=["POST"])
@token_required(role="admin")
def stress_test():
    filename = request.json.get("filename")
    duration = int(request.json.get("duration", 300))  # default 5 minutes

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    input_path = os.path.join(upload_folder, filename)

    if not os.path.exists(input_path):
        return jsonify({"error": "File not found"}), 404

    img = Image.open(input_path)
    start_time = time.time()
    counter = 0

    # Keep re-processing the same image until time is up
    while time.time() - start_time < duration:
        img = img.filter(ImageFilter.GaussianBlur(radius=5))
        img = img.rotate(15)  # rotate slightly so it evolves
        counter += 1

    # Save once at the end with a unique name
    result_folder = current_app.config["RESULT_FOLDER"]
    os.makedirs(result_folder, exist_ok=True)
    out_name = unique_filename("stress", filename, result_folder)
    out_path = os.path.join(result_folder, out_name)
    img.save(out_path)

    record = save_results_metadata(filename, out_name, g.user)
    return jsonify({
        "message": f"Stress test completed on {filename}",
        "result": out_name,
        "iterations": counter,
        "metadata": record
    }), 200