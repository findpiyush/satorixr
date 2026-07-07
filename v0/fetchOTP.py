import imaplib
import email
import re
import os
import time
from dotenv import load_dotenv

load_dotenv()

def fetch_latest_otp(email_address, password, imap_server="imap.gmail.com"):
    """
    Fetches the latest OTP from the given email inbox.
    """
    try:
        # connect to imap server
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_address, password)
        mail.select("inbox")

        status, messages = mail.search(None, 'ALL')
        if status != "OK" or not messages or not messages[0]:
            print("No messages found in inbox.")
            return None

        email_ids = messages[0].split()
        if not email_ids:
            print("No message IDs returned by IMAP search.")
            return None

        # Traverse from newest to oldest until we find a valid OTP.
        for email_id in reversed(email_ids):
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            if status != "OK":
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = msg.get('subject', '') or ''
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type in ("text/plain", "text/html"):
                                payload = part.get_payload(decode=True)
                                if payload:
                                    body += payload.decode(errors="ignore")
                    else:
                        payload = msg.get_payload(decode=True)
                        if payload:
                            body = payload.decode(errors="ignore")

                    text_body = re.sub(r'<[^>]+>', ' ', body)
                    text_body = re.sub(r'\s+', ' ', text_body).strip()

                    # Prefer a 6-digit code near common OTP markers.
                    keyword_regex = re.compile(r'(verification code|verify code|verification|verify|OTP)[^\d]{0,40}(\d{6})', re.I)
                    keyword_match = keyword_regex.search(text_body)
                    if keyword_match:
                        return keyword_match.group(2)

                    # Fallback to any 6-digit string in the message body.
                    fallback_match = re.search(r'\b(\d{6})\b', text_body)
                    if fallback_match:
                        return fallback_match.group(1)

        print("No OTP email found.")
        return None

    except Exception as e:
        print(f"Error fetching OTP: {e}")
        return None
    finally:
        try:
            mail.close()
            mail.logout()
        except:
            pass

if __name__ == "__main__":
    EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD") 
    
    print("Fetching OTP...")
    otp = fetch_latest_otp(EMAIL_ADDRESS, EMAIL_PASSWORD)
    if otp:
        print(f"Extracted OTP: {otp}")