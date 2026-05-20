import os
import imaplib
import email
import argparse
import email.utils
from email.header import decode_header
from dotenv import load_dotenv
from ai_analyzer import analyze_emails
from email_manager import EmailManager

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
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
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

def check_inbox(language='en', limit=10):
    emails_data = [] 
    limit = min(limit, 10)

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select('inbox')
        
        status, response = mail.search(None, 'UNSEEN')
        email_ids = response[0].split()
        unread_count = len(email_ids)
        print(MESSAGES[language]['success'].format(count=unread_count))
        
        latest_emails = email_ids[-limit:] 
        
        for e_id in latest_emails:
            status, msg_data = mail.fetch(e_id, '(BODY.PEEK[])')
            for response_part in msg_data:
                
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    sender = clean_text(msg.get("From"))
                    subject = clean_text(msg.get("Subject"))
                    
                    raw_date = msg.get("Date")
                    try:
                        parsed_date = email.utils.parsedate_to_datetime(raw_date)
                        date_str = parsed_date.strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        date_str = str(raw_date)
                    
                    full_body = get_email_body(msg)
                    
                    emails_data.append({
                        "id": e_id,
                        "sender": sender,
                        "subject": subject,
                        "date": date_str,
                        "body": full_body
                    })
        
        return emails_data, mail 

    except Exception as e:
        print(MESSAGES[language]['error'].format(error=e))
        return [], None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and analyze emails for AI Inbox Triage")
    parser.add_argument("--lang", choices=["en", "pl"], default="en", help="Select UI language (en or pl)")
    parser.add_argument("--limit", type=int, default=10, help="Limit pobieranych wiadomości (max 10)")
    args = parser.parse_args()

    fetched_data, mail_connection = check_inbox(language=args.lang, limit=args.limit)

    if fetched_data and mail_connection:
        manager = EmailManager(mail_connection, lang=args.lang)

        if args.lang == "pl":
            print(f"\n[System] Pobrano do pamięci {len(fetched_data)} wiadomości gotowych do analizy.")
            print("[AI] Rozpoczynam analizę...")
            print("\n" + "="*50)
            print("         RAPORT AI INBOX TRIAGE")
            print("="*50)
        else:
            print(f"\n[System] Fetched {len(fetched_data)} messages ready for analysis.")
            print("[AI] Starting analysis...")
            print("\n" + "="*50)
            print("         AI INBOX TRIAGE REPORT")
            print("="*50)

        for email_data in fetched_data:

            report = analyze_emails([email_data], lang=args.lang)
            
            if args.lang == "pl":
                print(f"\n--- Wynik AI ---\n{report}")
            else:
                print(f"\n--- AI Analysis ---\n{report}")


            if args.lang == "pl":
                prompt = "Wybierz akcję: [K] Kosz | [A] Archiwum | [P] Przeczytane | [Z] Zignoruj: "
            else:
                prompt = "Action: [T] Trash | [A] Archive | [R] Read | [I] Ignore: "
            
            decision = input(prompt).strip().lower()
            
            if decision in ['k', 't']: 
                status = manager.trash_email(email_data["id"])
                print(f"🗑️ {status}")
            elif decision == 'a':
                status = manager.archive_email(email_data["id"])
                print(f"📦 {status}")
            elif decision in ['p', 'r']:
                status = manager.mark_as_read(email_data["id"])
                print(f"👁️ {status}")
            else:
                print("⏭️ Zignorowano." if args.lang == "pl" else "⏭️ Ignored.")
            
            print("-" * 50)

        mail_connection.expunge()
        
        print("\n" + "="*50)
        empty_prompt = "🗑️ Czy chcesz trwale opróżnić Kosz ze wszystkich starych wiadomości? (t/N): " if args.lang == "pl" else "🗑️ Empty Trash completely? (y/N): "
        if input(empty_prompt).strip().lower() in ['t', 'y']:
            print(manager.empty_trash())

        mail_connection.logout()
        
        if args.lang == "pl":
            print("\n[System] Zakończono procesowanie. Wylogowano.")
        else:
            print("\n[System] Processing complete. Logged out.")
        print("="*50)