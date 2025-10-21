import os
import time
import uuid
import shutil
import tempfile
from flask import Blueprint, request, jsonify, session
from PIL import Image, ImageFilter, ImageOps
from app.services import s3, ddb

process_bp = Blueprint("process", __name__)


def unique_filename(prefix, original_name):
    """Generate a unique filename with timestamp and UUID."""
    base, ext = os.path.splitext(original_name)
    candidate = f"{prefix}_{base}_{int(time.time())}_{uuid.uuid4().hex[:6]}{ext}"
    print(f"[DEBUG] Generated unique filename: {candidate}")
    return candidate


@process_bp.route("/", methods=["POST"])
def process_image():
    """Handle image processing requests from the API service."""
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
            flip_type = operations["flip"].lower()
            if flip_type == "horizontal":
                img = ImageOps.mirror(img)
            elif flip_type == "vertical":
                img = ImageOps.flip(img)

        out_name = unique_filename("processed", filename)
        tmp_out = os.path.join(tmp_dir, out_name)
        img.save(tmp_out)

        s3_key = f"results/{out_name}"
        s3.upload_file_to_s3(tmp_out, s3_key)

        user = session.get("user", {})
        record = ddb.save_result_metadata(
            filename,
            out_name,
            {
                "username": user.get("cognito:username"),
                "role": "admin" if user.get("cognito:username") == "admin1" else "user"
            }
        )
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
