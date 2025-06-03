from flask import Blueprint, jsonify, request
from Utils.auth_required import auth_required
from url_check import check_link
from email_check import check_email_breaches

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

@scan_bp.route("/link-check", methods=["GET","POST"])
@auth_required
def scan_link():
    url = request.args.get("url") if request.method == 'GET' else request.json.get("url")

    if not url:
        return jsonify({"error": "URL is required"}), 400
    else:
        data, status = check_link(url)
        return jsonify(data), status

@scan_bp.route("/wifi", methods=["POST"])
# @auth_required
def scan_wifi():
    # TODO: Trigger local WiFi scan
    return jsonify({"message": "WiFi scan started", "status": "in_progress", "scan_id": "mock-scan-id"}), 200

@scan_bp.route("/shodan", methods=["POST"])
# @auth_required
def scan_shodan():
    # TODO: Extract IP and call shodan_scan()
    return jsonify({"message": "Shodan scan started"}), 200
