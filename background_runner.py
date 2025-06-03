import threading
import time
import os
from email_scanner import scan_inbox

def loop():
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")

    while True:
        flagged_emails = scan_inbox(email_user, email_pass)
        if flagged_emails:
            print("Spam detected:")
            for f in flagged_emails:
                print(f)
        time.sleep(300) 

def start_background_scan():
    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
