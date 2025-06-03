import os
import imaplib
import email
import json
import requests
from flask import Blueprint, g, jsonify
from email.header import decode_header
from datetime import datetime
from dotenv import load_dotenv
from Utils.auth_required import auth_required
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

load_dotenv()

AISPAMCHECK_API_KEY = os.getenv("AISPAMCHECK_API_KEY")

email_scan_bp = Blueprint("email_scan_bp", __name__)


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


def save_to_file(data, file_path="flagged_spam.json"):
    timestamped_data = {
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    try:
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump([timestamped_data], f, indent=4)
        else:
            with open(file_path, "r+", encoding="utf-8") as f:
                existing = json.load(f)
                existing.append(timestamped_data)
                f.seek(0)
                json.dump(existing, f, indent=4)
    except Exception as e:
        print(f"Failed to write to {file_path}: {e}")


tokenizer = AutoTokenizer.from_pretrained("cybersectony/phishing-email-detection-distilbert_v2.4.1")
model = AutoModelForSequenceClassification.from_pretrained("cybersectony/phishing-email-detection-distilbert_v2.4.1")

def detect_phishing(msg):
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

    try:
        # Tokenize and predict
        inputs = tokenizer(combined_text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        probs = predictions[0].tolist()

        # Map index to class labels
        labels = {
            "legitimate_email": probs[0],
            "phishing_url": probs[1],
            "legitimate_url": probs[2],
            "phishing_url_alt": probs[3]
        }

        prediction, confidence = max(labels.items(), key=lambda x: x[1])

        if "phishing" in prediction:
            return {
                "from": from_,
                "subject": subject,
                "flags": [f"PHISHING: {prediction.replace('_', ' ')} ({confidence:.2%} confidence)"]
            }
    except Exception as e:
        print(f"Error with phishing detection model: {e}")

    return None


def scan_inbox(email_user, email_pass):
    mail = connect_to_email(email_user, email_pass)
    if not mail:
        return []

    msgs = fetch_recent_emails(mail, limit=10)
    flagged = []

    for msg in msgs:
        spam_result = detect_spam(msg)
        if spam_result:
            flagged.append(spam_result)
            save_to_file(spam_result)

        phishing_result = detect_phishing(msg)
        if phishing_result:
            flagged.append(phishing_result)
            save_to_file(phishing_result)


    mail.logout()
    return flagged


@email_scan_bp.route("/scan", methods=["GET"])
@auth_required
def scan_emails_route():
    auth_user = g.user
    if not auth_user:
        return jsonify({"error": "Unauthorized"}), 401

    email_user = auth_user.get("email")
    email_pass = auth_user.get("email_pass")

    if not email_user or not email_pass:
        return jsonify({"error": "Missing email credentials"}), 400

    results = scan_inbox(email_user, email_pass)
    return jsonify({"flagged_emails": results}), 200
