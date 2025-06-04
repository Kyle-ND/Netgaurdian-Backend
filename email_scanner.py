#the name of this file is emal_scanner.py its using scan_bp which has already bean used rename it and tell me where else to rename it

import os
import imaplib
import email
import requests
from flask import Blueprint, g, jsonify, request
from email.header import decode_header
from dotenv import load_dotenv
from Utils.auth_required import auth_required

load_dotenv()

AISPAMCHECK_API_KEY = os.getenv("AISPAMCHECK_API_KEY")

email_scan_bp = Blueprint("email_scan", __name__)


def connect_to_email(email_user, email_pass):
    try:
        mail = imaplib.IMAP4_SSL(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT", 993)))
        mail.login(email_user, email_pass)
        return mail
    except Exception as e:
        print(f"IMAP connection failed: {e}")
        return None


def fetch_recent_emails(mail, limit=10):
    mail.select("inbox")
    result, data = mail.search(None, "ALL")
    if result != "OK":
        return []

    email_ids = data[0].split()[-limit:]
    emails = []

    for eid in email_ids:
        res, msg_data = mail.fetch(eid, "(RFC822)")
        if res != "OK":
            continue
        msg = email.message_from_bytes(msg_data[0][1])
        emails.append(msg)

    return emails


def decode_mime_words(s):
    if not s:
        return ""
    decoded = decode_header(s)
    return ' '.join([
        str(part[0], part[1] or 'utf-8') if isinstance(part[0], bytes) else part[0]
        for part in decoded
    ])


def detect_spam(msg):
    subject = decode_mime_words(msg.get("Subject", ""))
    from_ = decode_mime_words(msg.get("From", ""))

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode(errors='ignore')
                    break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(errors='ignore')

    combined_text = f"{subject}\n{body}"

    url = "https://api.aispamcheck.com/api/v1/check"
    headers = {
        "Authorization": f"Bearer {AISPAMCHECK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"text": combined_text}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        if result.get("is_spam"):
            return {
                "from": from_,
                "subject": subject,
                "flags": ["AISPAMCHECK: Detected as spam"]
            }
    except Exception as e:
        print(f"Error with AISPAMCHECK API: {e}")

    return None


def scan_inbox(email_user, email_pass):
    mail = connect_to_email(email_user, email_pass)
    if not mail:
        return []

    msgs = fetch_recent_emails(mail, limit=10)
    flagged = []

    for msg in msgs:
        result = detect_spam(msg)
        if result:
            flagged.append(result)

    mail.logout()
    return flagged


@email_scan_bp.route("/scan", methods=["GET"])
@auth_required
def scan_emails_route():
    auth_user = g.user
    if not auth_user:
        return jsonify({"error": "Unauthorized"}), 401
    request_data = request.get_json()
    email_user = request_data.get("email")
    email_pass = request_data.get("email_pass")
    print(f"Scanning emails for user: {email_user}")
    print(email_pass)

    if not email_user or not email_pass:
        return jsonify({"error": "Missing email credentials"}), 400

    results = scan_inbox(email_user, email_pass)
    return jsonify({"flagged_emails": results}), 200
