import os
import tempfile
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from app.utils.auth_helper import login_required
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
@login_required
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
        user = session.get("user", {})
        record = ddb.save_upload_metadata(filename, resolution, file_size, user)
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
@login_required
def list_uploads():
    print("[DEBUG] /upload/list (GET) hit")
    files = ddb.load_uploads()
    print(f"[DEBUG] Loaded {len(files)} uploads from DynamoDB")

    user = session.get("user", {})
    role = "admin" if user.get("cognito:username") == "admin1" else "user"

    # Restrict to user unless admin
    if role != "admin":
        before = len(files)
        username = user.get("cognito:username")
        files = [f for f in files if f.get("user") == username]
        print(f"[DEBUG] Filtered uploads for {username}: {before} → {len(files)}")

    # Query params
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    sort = request.args.get("sort", "timestamp")
    order = request.args.get("order", "desc")
    filter_user = request.args.get("user")
    filter_input = request.args.get("q")
    print(f"[DEBUG] Query params → page={page}, limit={limit}, sort={sort}, order={order}, "
          f"filter_user={filter_user}, filter_input={filter_input}")

    # Filtering
    if filter_user and role == "admin":
        before = len(files)
        files = [f for f in files if f.get("user", "").lower() == filter_user.lower()]
        print(f"[DEBUG] Filtered by user={filter_user}: {before} → {len(files)}")
    if filter_input:
        before = len(files)
        files = [
            f for f in files
            if filter_input.lower() in f.get("filename", "").lower()
            or filter_input.lower() in f.get("user", "").lower()
        ]
        print(f"[DEBUG] Filtered by input={filter_input}: {before} → {len(files)}")

    # Sorting
    reverse = (order == "desc")
    print(f"[DEBUG] Sorting uploads by {sort}, reverse={reverse}")
    if sort == "timestamp":
        files.sort(key=lambda f: f.get("timestamp", 0), reverse=reverse)
    else:
        files.sort(key=lambda f: str(f.get(sort, "")).lower(), reverse=reverse)

    # Pagination
    total = len(files)
    start = (page - 1) * limit
    end = start + limit
    paginated = files[start:end]
    print(f"[DEBUG] Pagination applied: total={total}, returning {len(paginated)} uploads")

    # Add presigned preview URLs
    for f in paginated:
        if "filename" in f:
            s3_key = f"uploads/{f['filename']}"
            f["preview_url"] = s3.generate_presigned_url(s3_key)

    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
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
@login_required
def delete_upload(filename):
    print(f"[DEBUG] /upload/{filename} (DELETE) hit")

    uploads = ddb.load_uploads()
    file_meta = next((f for f in uploads if f.get("filename") == filename), None)
    print(f"[DEBUG] Metadata lookup for {filename}: {file_meta}")

    if not file_meta:
        print("[DEBUG] Metadata not found")
        return jsonify({"error": "Metadata not found"}), 404

    user = session.get("user", {})
    role = "admin" if user.get("cognito:username") == "admin1" else "user"

    if role != "admin" and file_meta.get("user") != user.get("cognito:username"):
        print(f"[DEBUG] Permission denied for user {user.get('cognito:username')}")
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
@login_required
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
