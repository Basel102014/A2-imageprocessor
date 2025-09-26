import os
import tempfile
from flask import Blueprint, request, jsonify, g
from werkzeug.utils import secure_filename
from app.utils.auth_helper import token_required
from app.services import s3, ddb
from PIL import Image

upload_bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    ok = "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    print(f"[DEBUG] allowed_file('{filename}') → {ok}")
    return ok


# ---------- Upload ----------
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

        # Save to a temp path so we can inspect before uploading to S3
        tmp_dir = tempfile.mkdtemp()
        tmp_path = os.path.join(tmp_dir, filename)
        file.save(tmp_path)
        print(f"[DEBUG] Temporarily saved file: {tmp_path}")

        resolution = "Unknown"
        file_size = os.path.getsize(tmp_path)
        print(f"[DEBUG] File size: {file_size} bytes")
        try:
            with Image.open(tmp_path) as img:
                resolution = f"{img.width}x{img.height}"
                print(f"[DEBUG] Image resolution: {resolution}")
        except Exception as e:
            print(f"[DEBUG] Could not read image resolution: {e}")

        # Upload file to S3
        s3_key = f"uploads/{filename}"
        s3.upload_file_to_s3(tmp_path, s3_key)
        print(f"[DEBUG] Uploaded file to S3 at key={s3_key}")

        # Save metadata in DynamoDB
        record = ddb.save_upload_metadata(filename, resolution, file_size, g.user)
        record["s3_key"] = s3_key
        print(f"[DEBUG] Saved upload metadata to DynamoDB: {record}")

        return jsonify({
            "message": "File uploaded successfully",
            "metadata": record
        }), 201

    print("[DEBUG] Invalid file type")
    return jsonify({"error": "Invalid file type"}), 400


# ---------- List ----------
@upload_bp.route("/list", methods=["GET"])
@token_required()
def list_uploads():
    print("[DEBUG] /upload/list (GET) hit")
    files = ddb.load_uploads()
    print(f"[DEBUG] Loaded {len(files)} uploads from DynamoDB")

    # Restrict to user unless admin
    if g.role != "admin":
        before = len(files)
        files = [f for f in files if f.get("user") == g.user.get("username")]
        print(f"[DEBUG] Filtered uploads for {g.user.get('username')}: {before} → {len(files)}")

    # Pagination/sorting (basic version)
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    start = (page - 1) * limit
    end = start + limit
    paginated = files[start:end]
    print(f"[DEBUG] Pagination applied: total={len(files)}, returning {len(paginated)}")

    return jsonify({
        "page": page,
        "limit": limit,
        "total": len(files),
        "results": paginated
    })


# ---------- Download ----------
@upload_bp.route("/<filename>", methods=["GET"])
def get_upload(filename):
    print(f"[DEBUG] /upload/{filename} (GET) hit")
    s3_key = f"uploads/{filename}"
    url = s3.generate_presigned_url(s3_key)
    print(f"[DEBUG] Generated presigned URL for {filename}: {url}")
    return jsonify({"download_url": url})


# ---------- Delete ----------
@upload_bp.route("/<filename>", methods=["DELETE"])
@token_required()
def delete_upload(filename):
    print(f"[DEBUG] /upload/{filename} (DELETE) hit")

    uploads = ddb.load_uploads()
    file_meta = next((f for f in uploads if f.get("filename") == filename), None)
    print(f"[DEBUG] Metadata lookup for {filename}: {file_meta}")

    if not file_meta:
        print("[DEBUG] Metadata not found")
        return jsonify({"error": "Metadata not found"}), 404

    if g.role != "admin" and file_meta.get("user") != g.user.get("username"):
        print(f"[DEBUG] Permission denied for user {g.user.get('username')}")
        return jsonify({"error": "Permission denied"}), 403

    try:
        s3_key = f"uploads/{filename}"
        s3.delete_file_from_s3(s3_key)
        print(f"[DEBUG] Deleted file from S3: {s3_key}")
        ddb.delete_upload_metadata(file_meta["id"])
        print(f"[DEBUG] Deleted metadata from DynamoDB: {file_meta['id']}")
        return jsonify({"message": f"File '{filename}' deleted successfully"}), 200
    except Exception as e:
        print(f"[DEBUG] Error deleting upload: {e}")
        return jsonify({"error": str(e)}), 500


# ---------- Clear ----------
@upload_bp.route("/clear", methods=["DELETE"])
@token_required(role="admin")
def clear_uploads():
    print("[DEBUG] /upload/clear (DELETE) hit")
    try:
        s3.clear_prefix("uploads/")
        print("[DEBUG] Cleared all uploads from S3")
        ddb.clear_uploads()
        print("[DEBUG] Cleared all upload metadata from DynamoDB")
        return jsonify({"message": "All uploads and metadata cleared"}), 200
    except Exception as e:
        print(f"[DEBUG] Error clearing uploads: {e}")
        return jsonify({"error": str(e)}), 500