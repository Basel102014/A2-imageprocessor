import os
from flask import Blueprint, jsonify, send_from_directory, current_app, request
from app.utils.auth import token_required
from app.utils.data_store import load_metadata

results_bp = Blueprint("results", __name__)

@results_bp.route("/", methods=["GET"])
@token_required
def list_results():
    result_folder = current_app.config["RESULT_FOLDER"]
    os.makedirs(result_folder, exist_ok=True)

    files = os.listdir(result_folder)
    return jsonify({"results": files})


@results_bp.route("/<filename>", methods=["GET"])
def get_result(filename):
    result_folder = current_app.config["RESULT_FOLDER"]
    if not os.path.exists(os.path.join(result_folder, filename)):
        return jsonify({"error": "File not found"}), 404

    return send_from_directory(result_folder, filename)

@results_bp.route("/metadata", methods=["GET"])
def get_metadata():
    return jsonify({"metadata": load_metadata()})