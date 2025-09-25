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
            print(f"[DEBUG] Generated unique filename: {candidate}")
            return candidate


# ---------------- Normal Processing ----------------
@process_bp.route("/", methods=["POST"])
@token_required()
def process_image():
    print("[DEBUG] /process route hit (POST)")
    data = request.json
    print(f"[DEBUG] Incoming request data: {data}")

    filename = data.get("filename")
    operations = data.get("operations", {})
    print(f"[DEBUG] Filename: {filename}, Operations: {operations}")

    if not filename:
        print("[DEBUG] No filename provided → 400")
        return jsonify({"error": "Filename required"}), 400

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    result_folder = current_app.config["RESULT_FOLDER"]

    input_path = os.path.join(upload_folder, filename)
    if not os.path.exists(input_path):
        print(f"[DEBUG] File not found at path: {input_path}")
        return jsonify({"error": "File not found"}), 404

    os.makedirs(result_folder, exist_ok=True)
    print(f"[DEBUG] Result folder ensured: {result_folder}")

    try:
        img = Image.open(input_path)
        print(f"[DEBUG] Opened image: {input_path}, size={img.size}, mode={img.mode}")

        # --- Apply operations ---
        if "rotate" in operations:
            angle = float(operations["rotate"])
            print(f"[DEBUG] Applying rotate: {angle}")
            img = img.rotate(angle, expand=True)

        if "blur" in operations:
            radius = float(operations["blur"])
            print(f"[DEBUG] Applying blur: radius={radius}")
            img = img.filter(ImageFilter.GaussianBlur(radius=radius))

        if "resize" in operations:
            resize_conf = operations["resize"]
            w = int(resize_conf.get("width", img.width))
            h = int(resize_conf.get("height", img.height))
            print(f"[DEBUG] Applying resize: ({w}, {h})")
            img = img.resize((w, h))

        if "upscale" in operations:
            factor = float(operations["upscale"])
            w, h = int(img.width * factor), int(img.height * factor)
            print(f"[DEBUG] Applying upscale by factor {factor}: new size=({w}, {h})")
            img = img.resize((w, h))

        if operations.get("grayscale"):
            print("[DEBUG] Applying grayscale")
            img = ImageOps.grayscale(img)

        if "flip" in operations:
            mode = operations["flip"].lower()
            print(f"[DEBUG] Applying flip: {mode}")
            if mode == "horizontal":
                img = ImageOps.mirror(img)
            elif mode == "vertical":
                img = ImageOps.flip(img)

        # --- Save output with unique name ---
        out_name = unique_filename("processed", filename, result_folder)
        out_path = os.path.join(result_folder, out_name)
        img.save(out_path)
        print(f"[DEBUG] Saved processed image: {out_path}")

        record = save_results_metadata(filename, out_name, g.user)
        print(f"[DEBUG] Saved metadata: {record}")

        return jsonify({
            "message": f"Processed {filename}",
            "result": out_name,
            "metadata": record
        }), 200

    except Exception as e:
        print(f"[DEBUG] Processing failed: {e}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500


# ---------------- Stress Test ----------------
def worker_task(input_path, duration, output_path):
    """Repeatedly process the image for a given duration, save one final result."""
    print(f"[DEBUG] Worker started for {duration}s → input={input_path}, output={output_path}")
    end_time = time.time() + duration
    img = Image.open(input_path)

    while time.time() < end_time:
        img = img.rotate(45)
        img = img.filter(ImageFilter.GaussianBlur(5))
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    img.save(output_path)
    print(f"[DEBUG] Worker finished, saved output: {output_path}")


@process_bp.route("/stress", methods=["POST"])
@token_required()
def stress_test():
    """Stress test using all CPU cores by repeatedly processing an image."""
    print("[DEBUG] /stress route hit (POST)")
    data = request.json
    print(f"[DEBUG] Incoming request data: {data}")

    filename = data.get("filename")
    duration = int(data.get("duration", 30))
    print(f"[DEBUG] Stress test params → filename: {filename}, duration: {duration}s")

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    result_folder = current_app.config["RESULT_FOLDER"]

    input_path = os.path.join(upload_folder, filename)
    if not os.path.exists(input_path):
        print(f"[DEBUG] File not found at path: {input_path}")
        return jsonify({"error": "File not found"}), 404

    os.makedirs(result_folder, exist_ok=True)
    print(f"[DEBUG] Result folder ensured: {result_folder}")

    num_workers = multiprocessing.cpu_count()
    print(f"[DEBUG] Launching stress test with {num_workers} workers")
    processes = []
    outputs = []

    for i in range(num_workers):
        out_name = unique_filename(f"stress{i}", filename, result_folder)
        out_path = os.path.join(result_folder, out_name)
        outputs.append(out_name)

        print(f"[DEBUG] Starting worker {i} → output={out_name}")
        p = multiprocessing.Process(target=worker_task, args=(input_path, duration, out_path))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
    print("[DEBUG] All workers completed")

    # Save metadata for each worker’s result
    for out in outputs:
        print(f"[DEBUG] Saving metadata for output: {out}")
        save_results_metadata(filename, out, {"username": "stress-test", "timestamp": int(time.time())})

    return jsonify({
        "message": f"Stress test completed for {duration}s",
        "cores_used": num_workers,
        "results": outputs
    })
