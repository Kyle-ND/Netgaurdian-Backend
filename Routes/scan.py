from flask import Blueprint, jsonify, request,g
from Utils.auth_required import auth_required
from url_check import check_link
from email_check import check_email_breaches
from wifi_scanner_service import local_wifi_scan

import threading
import uuid
scan_bp = Blueprint("scan", __name__)

@scan_bp.route("/email", methods=["POST"])
@auth_required
def scan_email():
    email = request.args.get("email") if request.method == 'GET' else request.json.get("email")

    if not email:
        return jsonify({"error": "email is required"}), 400
    else:
        data, status = check_email_breaches(email)
        return jsonify(data), status

@scan_bp.route("/wifi", methods=["POST"])
@auth_required
def scan_wifi():
    thread = threading.Thread(target=local_wifi_scan(g.user), daemon=True)
    thread.start()
    return jsonify({"message": "WiFi scan started", "status": "in_progress"}), 200


@scan_bp.route("/extension-scan", methods=["POST"])
# @auth_required
def scan_extension():
    request_data = request.get_json()
    if not request_data or "url" not in request_data:
        return jsonify({"error": "URL is required"}), 400
    check_link = request_data.get("url")
    return check_link
