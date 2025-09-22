from flask import Blueprint, jsonify

upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/", methods=["GET"])
def test_upload():
    return jsonify({"message": "upload route alive"})
