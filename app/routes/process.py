import time
import uuid
import multiprocessing
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
        candidate = f"{prefix}_{base}_{int(time.time())}_{uuid.uuid4().hex[:6]}{ext}"
        if not os.path.exists(os.path.join(result_folder, candidate)):
            return candidate


# ---------------- Normal Processing ----------------
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


# ---------------- Stress Test ----------------
def worker_task(input_path, duration, output_path):
    """Repeatedly process the image for a given duration, save one final result."""
    end_time = time.time() + duration
    img = Image.open(input_path)

    while time.time() < end_time:
        img = img.rotate(45)
        img = img.filter(ImageFilter.GaussianBlur(5))
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    # Save the final processed image from this worker
    img.save(output_path)


@process_bp.route("/stress", methods=["POST"])
@token_required()
def stress_test():
    """Stress test using all CPU cores by repeatedly processing an image."""
    data = request.json
    filename = data.get("filename")
    duration = int(data.get("duration", 30))

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    result_folder = current_app.config["RESULT_FOLDER"]

    input_path = os.path.join(upload_folder, filename)
    if not os.path.exists(input_path):
        return jsonify({"error": "File not found"}), 404

    os.makedirs(result_folder, exist_ok=True)

    num_workers = multiprocessing.cpu_count()
    processes = []
    outputs = []

    for i in range(num_workers):
        out_name = unique_filename(f"stress{i}", filename, result_folder)
        out_path = os.path.join(result_folder, out_name)
        outputs.append(out_name)

        p = multiprocessing.Process(target=worker_task, args=(input_path, duration, out_path))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    # Save metadata for each worker’s result
    for out in outputs:
        save_results_metadata(filename, out, {"username": "stress-test", "timestamp": int(time.time())})

    return jsonify({
        "message": f"Stress test completed for {duration}s",
        "cores_used": num_workers,
        "results": outputs
    })
