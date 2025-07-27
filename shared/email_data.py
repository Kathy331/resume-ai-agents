from imapclient import IMAPClient
import email
from email.header import decode_header
from dotenv import load_dotenv
import os
import sys

# Load variables from .env
load_dotenv()

EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")
FOLDER = os.getenv("INTERVIEW_FOLDER")  # No default — must be set explicitly

# Optional Google credentials (not used here, just loaded)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")

def decode_mime_words(header_value):
    """Decode email subject or from headers properly"""
    decoded = decode_header(header_value)
    return ''.join([
        part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
        for part, encoding in decoded
    ])

def read_all_emails(folder):
    if not folder:
        print("!!!! ERROR: 'INTERVIEW_FOLDER' not set in .env file.")
        sys.exit(1)

    with IMAPClient('imap.gmail.com', use_uid=True, ssl=True) as server:
        try:
            server.login(EMAIL, PASSWORD)
        except Exception as e:
            print(f"!!!! ERROR: Login failed: {e}")
            sys.exit(1)

        try:
            server.select_folder(folder, readonly=True)
        except Exception as e:
            print(f"!!!! ERROR: Could not select folder '{folder}': {e}")
            sys.exit(1)

        print(f"!!!! Reading all emails from folder: {folder}\n")

        messages = server.search(['ALL'])  # Fetch all messages

        if not messages:
            print("!!!! No emails found.")
            return

        response = server.fetch(messages, ['RFC822'])

        for _, data in response.items():
            raw_email = data[b'RFC822']
            email_message = email.message_from_bytes(raw_email)

            subject = decode_mime_words(email_message.get('Subject', ''))
            from_ = decode_mime_words(email_message.get('From', ''))

            print(f"From: {from_}")
            print(f"Subject: {subject}")

            # Extract plain text body
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain' and not part.get('Content-Disposition'):
                        body = part.get_payload(decode=True).decode(errors='replace')
                        print(f"Body:\n{body.strip()}\n{'-'*50}\n")
                        break
            else:
                body = email_message.get_payload(decode=True).decode(errors='replace')
                print(f"Body:\n{body.strip()}\n{'-'*50}\n")

if __name__ == "__main__":
    read_all_emails(FOLDER)
