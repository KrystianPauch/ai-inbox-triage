import os
import imaplib
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv('EMAIL_ADDRESS')
PASSWORD = os.getenv('EMAIL_PASSWORD')
IMAP_SERVER = 'imap.gmail.com'

MESSAGES = {
    "en": {
        "success": "Logged in successfully You have {count} unread messages.",
        "error": "Login failed: {error}"
},
    "pl": {
        "success": "Zalogowano pomyślnie! Masz {count} nieprzeczytanych wiadomości.",
        "error": "Błąd logowania: {error}"
    }
}

def check_inbox(language='en'):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select('inbox')
        status, response = mail.search(None, 'UNSEEN')
        email_ids = response[0].split()
        unread_count = len(email_ids)
        print(MESSAGES[language]['success'].format(count=unread_count))
        mail.logout()

    except Exception as e:
        print(MESSAGES[language]['error'].format(error=e))

if __name__ == "__main__":
    print("--- English UI ---")
    check_inbox(language='en')

    print("\n--- Polish UI ---")
    check_inbox(language='pl')