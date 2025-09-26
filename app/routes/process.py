import time
import uuid
import multiprocessing
import tempfile
import shutil
import os
from flask import Blueprint, request, jsonify, g
from PIL import Image, ImageFilter, ImageOps
from app.utils.auth_helper import login_required
from app.services import s3, ddb

process_bp = Blueprint("process", __name__)


def unique_filename(prefix, original_name):
    base, ext = os.path.splitext(original_name)
    candidate = f"{prefix}_{base}_{int(time.time())}_{uuid.uuid4().hex[:6]}{ext}"
    print(f"[DEBUG] Generated unique filename: {candidate}")
    return candidate


# ---------------- Normal Processing ----------------
@process_bp.route("/", methods=["POST"])
@login_required
def process_image():
    print("[DEBUG] /process route hit (POST)")
    data = request.json
    print(f"[DEBUG] Incoming request data: {data}")

    filename = data.get("filename")
    operations = data.get("operations", {})

    if not filename:
        return jsonify({"error": "Filename required"}), 400

    s3_input_key = f"uploads/{filename}"
    tmp_dir = tempfile.mkdtemp()
    tmp_in = os.path.join(tmp_dir, filename)

    try:
        s3.download_file_from_s3(s3_input_key, tmp_in)
        img = Image.open(tmp_in)
        print(f"[DEBUG] Opened image: size={img.size}, mode={img.mode}")

        # --- Apply operations ---
        if "rotate" in operations:
            img = img.rotate(float(operations["rotate"]), expand=True)
        if "blur" in operations:
            img = img.filter(ImageFilter.GaussianBlur(radius=float(operations["blur"])))
        if "resize" in operations:
            w = int(operations["resize"].get("width", img.width))
            h = int(operations["resize"].get("height", img.height))
            img = img.resize((w, h))
        if "upscale" in operations:
            factor = float(operations["upscale"])
            img = img.resize((int(img.width * factor), int(img.height * factor)))
        if operations.get("grayscale"):
            img = ImageOps.grayscale(img)
        if "flip" in operations:
            if operations["flip"].lower() == "horizontal":
                img = ImageOps.mirror(img)
            elif operations["flip"].lower() == "vertical":
                img = ImageOps.flip(img)

        # --- Save locally, upload to S3 ---
        out_name = unique_filename("processed", filename)
        tmp_out = os.path.join(tmp_dir, out_name)
        img.save(tmp_out)

        s3_key = f"results/{out_name}"
        s3.upload_file_to_s3(tmp_out, s3_key)

        record = ddb.save_result_metadata(filename, out_name, g.user)
        record["s3_key"] = s3_key

        return jsonify({
            "message": f"Processed {filename}",
            "result": out_name,
            "metadata": record
        }), 200

    except Exception as e:
        print(f"[DEBUG] Processing failed: {e}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ---------------- Stress Test ----------------
def worker_task(local_in, duration, local_out):
    print(f"[DEBUG] Worker started for {duration}s → {local_in}")
    end_time = time.time() + duration
    img = Image.open(local_in)

    while time.time() < end_time:
        img = img.rotate(45)
        img = img.filter(ImageFilter.GaussianBlur(5))
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    img.save(local_out)
    print(f"[DEBUG] Worker finished → {local_out}")


@process_bp.route("/stress", methods=["POST"])
@login_required
def stress_test():
    print("[DEBUG] /stress route hit (POST)")
    data = request.json
    filename = data.get("filename")
    duration = int(data.get("duration", 30))

    if not filename:
        return jsonify({"error": "Filename required"}), 400

    s3_input_key = f"uploads/{filename}"
    tmp_dir = tempfile.mkdtemp()
    tmp_in = os.path.join(tmp_dir, filename)

    try:
        s3.download_file_from_s3(s3_input_key, tmp_in)
        num_workers = multiprocessing.cpu_count()
        processes, outputs = [], []

        for i in range(num_workers):
            out_name = unique_filename(f"stress{i}", filename)
            tmp_out = os.path.join(tmp_dir, out_name)
            outputs.append(out_name)
            p = multiprocessing.Process(target=worker_task, args=(tmp_in, duration, tmp_out))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        for out in outputs:
            local_out = os.path.join(tmp_dir, out)
            s3_key = f"results/{out}"
            s3.upload_file_to_s3(local_out, s3_key)
            ddb.save_result_metadata(filename, out, {"username": "stress-test", "role": "system"})

        return jsonify({
            "message": f"Stress test completed for {duration}s",
            "cores_used": num_workers,
            "results": outputs
        })

    except Exception as e:
        print(f"[DEBUG] Stress test failed: {e}")
        return jsonify({"error": f"Stress test failed: {str(e)}"}), 500

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
