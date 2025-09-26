from flask import Blueprint, jsonify, request, session
from app.utils.auth_helper import login_required
from app.services import s3, ddb

results_bp = Blueprint("results", __name__)


@results_bp.route("/", methods=["GET"])
@login_required
def list_results():
    """List all result files stored in S3."""
    print("[DEBUG] /results/ (GET) hit → listing results from S3")
    files = s3.list_files_with_prefix("results/")
    print(f"[DEBUG] Files found in S3 results/: {files}")
    return jsonify({"results": files})


@results_bp.route("/<filename>", methods=["GET"])
def get_result(filename):
    """Generate a pre-signed URL to download a specific result file."""
    print(f"[DEBUG] /results/{filename} (GET) hit → presigned URL")
    s3_key = f"results/{filename}"
    url = s3.generate_presigned_url(s3_key)
    if not url:
        print(f"[DEBUG] File not found in S3: {s3_key}")
        return jsonify({"error": "File not found"}), 404
    print(f"[DEBUG] Generated presigned URL: {url}")
    return jsonify({"download_url": url})


@results_bp.route("/metadata", methods=["GET"])
@login_required
def get_metadata():
    """Get paginated, sortable, and filterable result metadata."""
    print("[DEBUG] /results/metadata (GET) hit")
    metadata = ddb.load_results()
    print(f"[DEBUG] Loaded metadata count: {len(metadata)}")

    user = session.get("user", {})
    role = "admin" if user.get("cognito:username") == "admin1" else "user"

    # Role-based filtering
    if role != "admin":
        before = len(metadata)
        username = user.get("cognito:username")
        metadata = [m for m in metadata if m.get("user") == username]
        print(f"[DEBUG] User '{username}' filtered metadata count: {before} → {len(metadata)}")

    # Query params
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 5))
    sort = request.args.get("sort", "timestamp")
    order = request.args.get("order", "desc")
    filter_user = request.args.get("user")
    filter_input = request.args.get("input")
    print(f"[DEBUG] Query params → page={page}, limit={limit}, sort={sort}, order={order}, "
          f"filter_user={filter_user}, filter_input={filter_input}")

    # Filtering
    if filter_user and role == "admin":
        before = len(metadata)
        metadata = [m for m in metadata if m.get("user", "").lower() == filter_user.lower()]
        print(f"[DEBUG] Filtered by user={filter_user}: {before} → {len(metadata)}")
    if filter_input:
        before = len(metadata)
        metadata = [
            m for m in metadata
            if filter_input.lower() in m.get("input", "").lower()
            or filter_input.lower() in m.get("user", "").lower()
        ]
        print(f"[DEBUG] Filtered by input={filter_input}: {before} → {len(metadata)}")

    # Sorting
    reverse = (order == "desc")
    print(f"[DEBUG] Sorting metadata by {sort}, reverse={reverse}")
    if sort == "timestamp":
        metadata.sort(key=lambda r: r.get("timestamp", ""), reverse=reverse)
    else:
        metadata.sort(key=lambda r: str(r.get(sort, "")).lower(), reverse=reverse)

    # Pagination
    total = len(metadata)
    start = (page - 1) * limit
    end = start + limit
    paginated = metadata[start:end]
    print(f"[DEBUG] Pagination applied: total={total}, returning {len(paginated)} results")

    # Add presigned preview URLs
    for m in paginated:
        if "output" in m:
            s3_key = f"results/{m['output']}"
            m["preview_url"] = s3.generate_presigned_url(s3_key)

    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "results": paginated
    })



@results_bp.route("/clear", methods=["DELETE"])
@login_required
def clear_results():
    """Delete all result files and metadata."""
    print("[DEBUG] /results/clear (DELETE) hit")
    try:
        s3.clear_prefix("results/")
        print("[DEBUG] Cleared all results from S3")
        ddb.clear_results()
        print("[DEBUG] Cleared all result metadata from DynamoDB")
        return jsonify({"message": "All results and metadata cleared"}), 200
    except Exception as e:
        print(f"[DEBUG] Error clearing results: {e}")
        return jsonify({"error": str(e)}), 500


@results_bp.route("/<filename>", methods=["DELETE"])
@login_required
def delete_result(filename):
    """Delete a specific result file and prune metadata."""
    print(f"[DEBUG] /results/{filename} (DELETE) hit")

    try:
        s3_key = f"results/{filename}"
        s3.delete_file_from_s3(s3_key)
        print(f"[DEBUG] Deleted file from S3: {s3_key}")

        # Delete metadata entry
        metadata = ddb.load_results()
        match = next((m for m in metadata if m.get("output") == filename), None)
        if match:
            ddb.delete_result_metadata(match["id"])
            print(f"[DEBUG] Deleted metadata from DynamoDB: {match['id']}")
        else:
            print(f"[DEBUG] No metadata entry found for {filename}")

        return jsonify({"message": f"Result '{filename}' deleted"}), 200
    except Exception as e:
        print(f"[DEBUG] Error deleting result: {e}")
        return jsonify({"error": str(e)}), 500
