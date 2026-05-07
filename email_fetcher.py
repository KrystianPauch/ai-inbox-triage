import os
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv('EMAIL_ADDRESS')
PASSWORD = os.getenv('EMAIL_PASSWORD')
IMAP_SERVER = 'imap.gmail.com'

MESSAGES = {
    "en": {
        "success": "Logged in successfully! You have {count} unread messages.",
        "error": "Login failed: {error}",
        "analysis": "--- Analyzing the last 3 messages ---",
        "sender": "Sender",
        "subject": "Subject"
    },
    "pl": {
        "success": "Zalogowano pomyślnie! Masz {count} nieprzeczytanych wiadomości.",
        "error": "Błąd logowania: {error}",
        "analysis": "--- Analiza ostatnich 3 wiadomości ---",
        "sender": "Nadawca",
        "subject": "Temat"
    }
}

def clean_text(text):
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

def check_inbox(language='en'):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select('inbox')
        
        status, response = mail.search(None, 'UNSEEN')
        email_ids = response[0].split()
        unread_count = len(email_ids)
        print(MESSAGES[language]['success'].format(count=unread_count))
        
        print(f"\n{MESSAGES[language]['analysis']}")
        latest_emails = email_ids[-3:] 
        
        for e_id in latest_emails:
            status, msg_data = mail.fetch(e_id, '(BODY.PEEK[])')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    sender = clean_text(msg.get("From"))
                    subject = clean_text(msg.get("Subject"))
                    
                    print(f"{MESSAGES[language]['sender']}: {sender}")
                    print(f"{MESSAGES[language]['subject']}: {subject}\n")
        
        mail.logout()

    except Exception as e:
        print(MESSAGES[language]['error'].format(error=e))

if __name__ == "__main__":
    print("--- English UI ---")
    check_inbox(language='en')
    
    print("\n--- Polish UI ---")
    check_inbox(language='pl')