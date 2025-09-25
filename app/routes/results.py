import os
import json
from flask import Blueprint, jsonify, send_from_directory, current_app, request, g
from app.utils.auth import token_required
from app.utils.data_store import load_results, DATA_FILE

results_bp = Blueprint("results", __name__)


@results_bp.route("/", methods=["GET"])
@token_required()
def list_results():
    """List all result files in the results folder."""
    result_folder = current_app.config["RESULT_FOLDER"]
    os.makedirs(result_folder, exist_ok=True)

    files = os.listdir(result_folder)
    return jsonify({"results": files})


@results_bp.route("/<filename>", methods=["GET"])
def get_result(filename):
    """Download a specific result file if it exists."""
    result_folder = current_app.config["RESULT_FOLDER"]
    file_path = os.path.join(result_folder, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_from_directory(result_folder, filename)


@results_bp.route("/metadata", methods=["GET"])
@token_required()
def get_metadata():
    """Get paginated, sortable, and filterable result metadata.
       - Normal users: only their own metadata
       - Admins: all metadata
    """
    metadata = load_results()

    # Role-based filtering
    if g.user.get("role") != "admin":
        metadata = [m for m in metadata if m.get("user") == g.user.get("username")]

    # Query params
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 5))
    sort = request.args.get("sort", "timestamp")
    order = request.args.get("order", "desc")
    filter_user = request.args.get("user")
    filter_input = request.args.get("input")

    # Filtering (admins only for user filter)
    if filter_user and g.user.get("role") == "admin":
        metadata = [m for m in metadata if m.get("user", "").lower() == filter_user.lower()]
    if filter_input:
        metadata = [
            m for m in metadata
            if filter_input.lower() in m.get("input", "").lower()
            or filter_input.lower() in m.get("user", "").lower()
        ]

    # Sorting
    reverse = (order == "desc")
    if sort == "timestamp":
        metadata.sort(key=lambda r: r.get("timestamp", ""), reverse=reverse)
    else:
        metadata.sort(key=lambda r: str(r.get(sort, "")).lower(), reverse=reverse)

    # Pagination
    total = len(metadata)
    start = (page - 1) * limit
    end = start + limit
    paginated = metadata[start:end]

    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "results": paginated
    })


@results_bp.route("/clear", methods=["DELETE"])
@token_required(role="admin")
def clear_results():
    """Delete all result files and reset metadata."""
    result_folder = current_app.config["RESULT_FOLDER"]
    os.makedirs(result_folder, exist_ok=True)

    # Delete all result files
    for filename in os.listdir(result_folder):
        file_path = os.path.join(result_folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Delete metadata file
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

    return jsonify({"message": "All results and metadata cleared"}), 200


@results_bp.route("/<filename>", methods=["DELETE"])
@token_required(role="admin")
def delete_result(filename):
    """Delete a specific result file and prune metadata."""
    result_folder = current_app.config["RESULT_FOLDER"]
    file_path = os.path.join(result_folder, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        os.remove(file_path)

        # Remove entry from metadata
        metadata = load_results()
        metadata = [m for m in metadata if m.get("output") != filename]
        with open(DATA_FILE, "w") as f:
            json.dump(metadata, f, indent=2)

        return jsonify({"message": f"Result '{filename}' deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
