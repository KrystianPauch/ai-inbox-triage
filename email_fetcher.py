import os
import imaplib
import email
import argparse
from email.header import decode_header
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

EMAIL = os.getenv('EMAIL_ADDRESS')
PASSWORD = os.getenv('EMAIL_PASSWORD')
IMAP_SERVER = 'imap.gmail.com'

# Dictionary containing localized UI strings
MESSAGES = {
    "en": {
        "success": "Logged in successfully! You have {count} unread messages.",
        "error": "Login failed: {error}",
        "analysis": "--- Analyzing the last 3 messages ---",
        "sender": "Sender",
        "subject": "Subject",
        "body": "Body snippet"
    },
    "pl": {
        "success": "Zalogowano pomyślnie! Masz {count} nieprzeczytanych wiadomości.",
        "error": "Błąd logowania: {error}",
        "analysis": "--- Analiza ostatnich 3 wiadomości ---",
        "sender": "Nadawca",
        "subject": "Temat",
        "body": "Fragment treści"
    }
}

def clean_text(text):
    """Decodes email headers into a readable string."""
    if not text:
        return ""
    decoded_parts = decode_header(text)
    clean_string = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            clean_string += part.decode(encoding or "utf-8", errors="ignore")
        else:
            clean_string += part
    return clean_string

def get_email_body(msg):
    """Extracts the plain text body from an email message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            # Look exclusively for plain text and ignore attachments
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    body = part.get_payload(decode=True).decode()
                    break
                except Exception:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode()
        except Exception:
            pass
    return body.strip()

def check_inbox(language='en'):
    """Connects to the IMAP server, counts unread emails, and fetches the latest 3."""
    try:
        # Establish secure SSL connection
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select('inbox')
        
        # Search for unread messages
        status, response = mail.search(None, 'UNSEEN')
        email_ids = response[0].split()
        unread_count = len(email_ids)
        print(MESSAGES[language]['success'].format(count=unread_count))
        
        print(f"\n{MESSAGES[language]['analysis']}")
        latest_emails = email_ids[-3:] 
        
        # Fetch and process the latest emails
        for e_id in latest_emails:
            # Use PEEK to avoid marking emails as read
            status, msg_data = mail.fetch(e_id, '(BODY.PEEK[])')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    sender = clean_text(msg.get("From"))
                    subject = clean_text(msg.get("Subject"))
                    
                    full_body = get_email_body(msg)
                    body_snippet = full_body[:100].replace('\n', ' ') + "..." if len(full_body) > 100 else full_body
                    
                    print(f"{MESSAGES[language]['sender']}: {sender}")
                    print(f"{MESSAGES[language]['subject']}: {subject}")
                    print(f"{MESSAGES[language]['body']}: {body_snippet}\n")
        
        # Safely close the connection
        mail.logout()

    except Exception as e:
        print(MESSAGES[language]['error'].format(error=e))

if __name__ == "__main__":
    # Setup command-line argument parsing
    parser = argparse.ArgumentParser(description="Fetch and analyze emails for AI Inbox Triage")
    parser.add_argument("--lang", choices=["en", "pl"], default="en", help="Select UI language (en or pl)")
    args = parser.parse_args()
    
    check_inbox(language=args.lang)