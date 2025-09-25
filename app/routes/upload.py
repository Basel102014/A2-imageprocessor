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
    ok = "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    print(f"[DEBUG] allowed_file('{filename}') → {ok}")
    return ok


@upload_bp.route("/", methods=["POST"])
@token_required()
def upload_file():
    print("[DEBUG] /upload (POST) hit → handling file upload")
    if "file" not in request.files:
        print("[DEBUG] No file part in request")
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]
    print(f"[DEBUG] Incoming file: {file.filename}")
    if file.filename == "":
        print("[DEBUG] No file selected")
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        print(f"[DEBUG] Secure filename: {filename}")

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)
        print(f"[DEBUG] Upload folder ensured: {upload_folder}")

        save_path = os.path.join(upload_folder, filename)
        file.save(save_path)
        print(f"[DEBUG] Saved file to: {save_path}")

        resolution = "Unknown"
        file_size = os.path.getsize(save_path)
        print(f"[DEBUG] File size: {file_size} bytes")
        try:
            with Image.open(save_path) as img:
                resolution = f"{img.width}x{img.height}"
                print(f"[DEBUG] Image resolution: {resolution}")
        except Exception as e:
            print(f"[DEBUG] Could not read image resolution: {e}")

        record = save_upload_metadata(filename, resolution, file_size, g.user)
        print(f"[DEBUG] Saved upload metadata: {record}")

        return jsonify({
            "message": "File uploaded successfully",
            "metadata": record
        }), 201

    print("[DEBUG] Invalid file type")
    return jsonify({"error": "Invalid file type"}), 400


@upload_bp.route("/list", methods=["GET"])
@token_required()
def list_uploads():
    print("[DEBUG] /upload/list (GET) hit")
    files = load_uploads()
    print(f"[DEBUG] Loaded {len(files)} uploads from metadata")

    if g.role != "admin":
        before = len(files)
        files = [f for f in files if f.get("user") == g.user.get("username")]
        print(f"[DEBUG] Filtered uploads for user={g.user.get('username')}: {before} → {len(files)}")

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    sort = request.args.get("sort", "filename")
    order = request.args.get("order", "asc")
    q = request.args.get("q")
    print(f"[DEBUG] Query params → page={page}, limit={limit}, sort={sort}, order={order}, q={q}")

    if q:
        before = len(files)
        files = [f for f in files if q.lower() in f["filename"].lower()]
        print(f"[DEBUG] Applied filename search filter '{q}': {before} → {len(files)}")

    reverse = (order == "desc")
    if sort == "resolution":
        print("[DEBUG] Sorting by resolution (pixels)")
        def res_key(f):
            try:
                w, h = map(int, f["resolution"].split("x"))
                return w * h
            except Exception:
                return 0
        files.sort(key=res_key, reverse=reverse)
    elif sort == "size":
        print("[DEBUG] Sorting by size (bytes)")
        files.sort(key=lambda f: f["size_bytes"], reverse=reverse)
    else:
        print(f"[DEBUG] Sorting by field: {sort}")
        files.sort(key=lambda f: str(f.get(sort, "")).lower(), reverse=reverse)

    total = len(files)
    start = (page - 1) * limit
    end = start + limit
    paginated = files[start:end]
    print(f"[DEBUG] Pagination applied: total={total}, returning {len(paginated)}")

    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "results": paginated
    })


@upload_bp.route("/<filename>", methods=["GET"])
def get_upload(filename):
    print(f"[DEBUG] /upload/{filename} (GET) hit → attempting to serve file")
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)

    if not os.path.exists(file_path):
        print(f"[DEBUG] File not found: {file_path}")
        return jsonify({"error": "File not found"}), 404

    print(f"[DEBUG] Serving file: {file_path}")
    return send_from_directory(upload_folder, filename)


@upload_bp.route("/<filename>", methods=["DELETE"])
@token_required()
def delete_upload(filename):
    print(f"[DEBUG] /upload/{filename} (DELETE) hit")
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)

    if not os.path.exists(file_path):
        print(f"[DEBUG] File not found for deletion: {file_path}")
        return jsonify({"error": "File not found"}), 404

    uploads = load_uploads()
    file_meta = next((f for f in uploads if f.get("filename") == filename), None)
    print(f"[DEBUG] Metadata lookup for {filename}: {file_meta}")

    if not file_meta:
        print("[DEBUG] Metadata not found")
        return jsonify({"error": "Metadata not found"}), 404

    if g.role != "admin" and file_meta.get("user") != g.user.get("username"):
        print(f"[DEBUG] Permission denied for user {g.user.get('username')}")
        return jsonify({"error": "Permission denied"}), 403

    try:
        os.remove(file_path)
        print(f"[DEBUG] Deleted file: {file_path}")
        prune_upload(filename)
        print(f"[DEBUG] Pruned metadata for: {filename}")
        return jsonify({"message": f"File '{filename}' deleted successfully"}), 200
    except Exception as e:
        print(f"[DEBUG] Error deleting upload: {e}")
        return jsonify({"error": str(e)}), 500


@upload_bp.route("/clear", methods=["DELETE"])
@token_required(role="admin")
def clear_uploads():
    """Delete all uploaded files and metadata (admin only)."""
    print("[DEBUG] /upload/clear (DELETE) hit → clearing all uploads")
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"[DEBUG] Deleted file: {file_path}")

    if os.path.exists(UPLOAD_DATA_FILE):
        os.remove(UPLOAD_DATA_FILE)
        print(f"[DEBUG] Deleted metadata file: {UPLOAD_DATA_FILE}")

    return jsonify({"message": "All uploads and metadata cleared"}), 200
