import os
import time
from flask import Blueprint, request, jsonify, current_app
from PIL import Image, ImageFilter

process_bp = Blueprint("process", __name__)

@process_bp.route("/", methods=["POST"])
def process_image():
    """
    Process an uploaded image from the uploads folder,
    apply CPU-heavy transformations, and save results.
    """
    filename = request.json.get("filename")
    if not filename:
        return jsonify({"error": "Filename required in JSON body"}), 400

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    result_folder = current_app.config["RESULT_FOLDER"]

    input_path = os.path.join(upload_folder, filename)
    if not os.path.exists(input_path):
        return jsonify({"error": "File not found"}), 404

    os.makedirs(result_folder, exist_ok=True)

    # Load image
    img = Image.open(input_path)

    processed_files = []
    iterations = int(request.json.get("iterations", 50))  # default 50 loops

    for i in range(iterations):
        # Apply transformations (CPU heavy if repeated many times)
        processed = img.filter(ImageFilter.GaussianBlur(radius=5))
        processed = processed.rotate(90)

        out_name = f"processed_{i}_{filename}"
        out_path = os.path.join(result_folder, out_name)
        processed.save(out_path)
        processed_files.append(out_name)

    return jsonify({
        "message": f"Processed {filename} {iterations} times",
        "results": processed_files
    }), 200
