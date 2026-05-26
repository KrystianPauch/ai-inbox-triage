import imaplib
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL_ADRESS") 
PASSWORD = os.getenv("EMAIL_PASSWORD") 
SERVER = os.getenv("IMAP_SERVER")

try:
    mail = imaplib.IMAP4_SSL(SERVER)
    mail.login(EMAIL, PASSWORD)
    typ, folders = mail.list()
    
    print("\n--- ZNALEZIONE FOLDERY ---")
    for f in folders:
        print(f.decode())
        
except Exception as e:
    print(f"Błąd: {e}")