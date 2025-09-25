import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.utils.auth import token_required
from PIL import Image

upload_bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/", methods=["POST"])
@token_required()
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        save_path = os.path.join(upload_folder, filename)
        file.save(save_path)

        # Gather metadata
        resolution = "Unknown"
        file_size = os.path.getsize(save_path)
        try:
            with Image.open(save_path) as img:
                resolution = f"{img.width}x{img.height}"
        except Exception:
            pass

        return jsonify({
            "message": "File uploaded successfully",
            "filename": filename,
            "path": save_path,
            "size_bytes": file_size,
            "resolution": resolution
        }), 201

    return jsonify({"error": "Invalid file type"}), 400


@upload_bp.route("/list", methods=["GET"])
@token_required()
def list_uploads():
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    files = []
    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        if os.path.isfile(file_path):
            try:
                with Image.open(file_path) as img:
                    resolution = f"{img.width}x{img.height}"
            except Exception:
                resolution = "Unknown"

            files.append({
                "filename": filename,
                "resolution": resolution,
                "size_bytes": os.path.getsize(file_path)
            })

    # Query params
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    sort = request.args.get("sort", "filename")
    order = request.args.get("order", "asc")
    q = request.args.get("q")  # filter by substring in filename

    # Filtering
    if q:
        files = [f for f in files if q.lower() in f["filename"].lower()]

    # Sorting
    reverse = (order == "desc")
    if sort == "resolution":
        def res_key(f):
            try:
                w, h = map(int, f["resolution"].split("x"))
                return w * h
            except Exception:
                return 0
        files.sort(key=res_key, reverse=reverse)
    elif sort == "size":
        files.sort(key=lambda f: f["size_bytes"], reverse=reverse)
    else:
        files.sort(key=lambda f: str(f.get(sort, "")).lower(), reverse=reverse)

    # Pagination
    total = len(files)
    start = (page - 1) * limit
    end = start + limit
    paginated = files[start:end]

    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "results": paginated
    })


@upload_bp.route("/<filename>", methods=["DELETE"])
@token_required(role="admin")
def delete_upload(filename):
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        os.remove(file_path)
        return jsonify({"message": f"File '{filename}' deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
