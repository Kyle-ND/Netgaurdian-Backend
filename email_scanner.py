import os
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 993))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


def connect_to_email():
    try:
        mail = imaplib.IMAP4_SSL(EMAIL_HOST, EMAIL_PORT)
        mail.login(EMAIL_USER, EMAIL_PASS)
        return mail
    except Exception as e:
        print(f"❌ IMAP connection failed: {e}")
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
    flags = []

    suspicious_subjects = ["win", "free", "urgent", "congratulations"]
    if any(word.lower() in subject.lower() for word in suspicious_subjects):
        flags.append("Suspicious subject")

    if "x-phishing" in str(msg).lower():
        flags.append("Phishing header")

    content_type = msg.get_content_type()
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body = part.get_payload(decode=True)
                if body and b"http" in body and b"verify" in body.lower():
                    flags.append("Link + verify combo")
    else:
        body = msg.get_payload(decode=True)
        if body and b"http" in body and b"verify" in body.lower():
            flags.append("Link + verify combo")

    return {
        "from": from_,
        "subject": subject,
        "flags": flags
    } if flags else None


def scan_inbox():
    mail = connect_to_email()
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
