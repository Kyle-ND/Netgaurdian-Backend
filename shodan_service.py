import imaplib
import email
from bs4 import BeautifulSoup
import re
from url_check import check_link

# Email credentials and server
IMAP_SERVER = 'imap.gmail.com'  # Use the correct IMAP server (e.g., for Outlook: outlook.office365.com)
EMAIL_ACCOUNT = 'zazisesib@gmail.com'
PASSWORD = 'osdtuqpkcheaukvp'  # Use an app password if 2FA is enabled

# Function to extract links
def extract_links(body):
    soup = BeautifulSoup(body, "html.parser")
    return [a['href'] for a in soup.find_all('a', href=True)]


# Connect to the IMAP server and login
def scan_email_links():
    
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, PASSWORD)

    # Select the mailbox (e.g., INBOX)
    mail.select("inbox")

# Search for all emails
    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()
    # Loop through the latest 5 emails
    for eid in email_ids[-5:]:
        status, msg_data = mail.fetch(eid, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = msg.get("Subject")
                from_ = msg.get("From")
                print(f"\n📧 From: {from_}")
                print(f"📌 Subject: {subject}")

                # Get email content
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/html":
                            body = part.get_payload(decode=True).decode(errors="ignore")
                            break
                else:
                    body = msg.get_payload(decode=True).decode(errors="ignore")

                links = extract_links(body)
                if links:
                    print("🔗 Links found:")
                    for link in links:
                        print(check_link(link))
                else:
                    print("❌ No links found.")

    # Logout
    mail.logout()




