from flask import Blueprint, jsonify

process_bp = Blueprint("process", __name__)

@process_bp.route("/", methods=["GET"])
def test_upload():
    return jsonify({"message": "process route alive"})
