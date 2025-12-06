import json
from flask import Blueprint, Response, jsonify, request

# PUBLIC BLUEPRINT
public_bp = Blueprint('public', __name__, url_prefix='/api/v1/public')

# ROUTE: HOME
@public_bp.route('/', methods=['GET'])
def return_home():
    return jsonify({
        "message": "Public API is live."
    })


# ❌ REMOVED: YOLO, OpenCV, PIL, Image Upload, Video Upload
# Because backend does NOT need AI detection for your accident app.


# Simple test route
@public_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok", "message": "Public API working"}), 200
