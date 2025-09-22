from flask import Blueprint, jsonify

results_bp = Blueprint("results", __name__)

@results_bp.route("/", methods=["GET"])
def test_upload():
    return jsonify({"message": "results route alive"})