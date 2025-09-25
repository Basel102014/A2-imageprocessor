import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory, g
from werkzeug.utils import secure_filename
from app.utils.auth import token_required
from app.utils.data_store import (
    save_upload_metadata,
    load_uploads,
    prune_upload,
    UPLOAD_DATA_FILE
)
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

        resolution = "Unknown"
        file_size = os.path.getsize(save_path)
        try:
            with Image.open(save_path) as img:
                resolution = f"{img.width}x{img.height}"
        except Exception:
            pass

        record = save_upload_metadata(filename, resolution, file_size, g.user)

        return jsonify({
            "message": "File uploaded successfully",
            "metadata": record
        }), 201

    return jsonify({"error": "Invalid file type"}), 400


@upload_bp.route("/list", methods=["GET"])
@token_required()
def list_uploads():
    files = load_uploads()

    if g.role != "admin":
        files = [f for f in files if f.get("user") == g.user.get("username")]

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    sort = request.args.get("sort", "filename")
    order = request.args.get("order", "asc")
    q = request.args.get("q")

    if q:
        files = [f for f in files if q.lower() in f["filename"].lower()]

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


@upload_bp.route("/<filename>", methods=["GET"])
def get_upload(filename):
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_from_directory(upload_folder, filename)


@upload_bp.route("/<filename>", methods=["DELETE"])
@token_required()
def delete_upload(filename):
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    uploads = load_uploads()
    file_meta = next((f for f in uploads if f.get("filename") == filename), None)

    if not file_meta:
        return jsonify({"error": "Metadata not found"}), 404

    if g.role != "admin" and file_meta.get("user") != g.user.get("username"):
        return jsonify({"error": "Permission denied"}), 403

    try:
        os.remove(file_path)
        prune_upload(filename)
        return jsonify({"message": f"File '{filename}' deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@upload_bp.route("/clear", methods=["DELETE"])
@token_required(role="admin")
def clear_uploads():
    """Delete all uploaded files and metadata (admin only)."""
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    # Delete all uploaded files
    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Delete metadata file
    if os.path.exists(UPLOAD_DATA_FILE):
        os.remove(UPLOAD_DATA_FILE)

    return jsonify({"message": "All uploads and metadata cleared"}), 200
