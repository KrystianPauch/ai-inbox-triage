import imaplib
import email
from email.header import decode_header
import email.utils
import re

class EmailManager:
    def __init__(self, mail_connection, lang="en"):
        """Inicjalizuje menedżer z aktywnym połączeniem IMAP."""
        self.mail = mail_connection
        self.lang = lang

    def archive_email(self, email_uid):
        """Przenosi wiadomość do archiwum za pomocą niezmiennego UID."""
        self.mail.select("INBOX", readonly=False)
        folder = '"[Gmail]/All Mail"' if self.lang == "en" else '"[Gmail]/Wszystkie"'
        
        self.mail.uid('COPY', email_uid, folder)
        self.mail.uid('STORE', email_uid, '+FLAGS', '\\Deleted')
        self.mail.expunge()

    def trash_email(self, email_uid):
        """Przenosi wiadomość do kosza za pomocą niezmiennego UID."""
        self.mail.select("INBOX", readonly=False)
        folder = '"[Gmail]/Trash"' if self.lang == "en" else '"[Gmail]/Kosz"'
        
        self.mail.uid('COPY', email_uid, folder)
        self.mail.uid('STORE', email_uid, '+FLAGS', '\\Deleted')
        self.mail.expunge()

    def mark_as_read(self, email_uid):
        """Oznacza wiadomość jako przeczytaną za pomocą niezmiennego UID."""
        self.mail.select("INBOX", readonly=False)
        self.mail.uid('STORE', email_uid, '+FLAGS', '\\Seen')

    def empty_trash(self, trash_folder=None):
        if trash_folder is None:
            trash_folder = '"[Gmail]/Trash"' if self.lang == "en" else '"[Gmail]/Kosz"'
        try:
            self.mail.select(trash_folder)
            status, response = self.mail.search(None, 'ALL')
            if status == 'OK' and response[0]:
                for e_id in response[0].split():
                    self.mail.store(e_id, '+FLAGS', '(\\Deleted)')
                self.mail.expunge()
            self.mail.select('INBOX')
            return "Kosz został trwale opróżniony." if self.lang == "pl" else "Trash emptied successfully."
        except Exception as e:
            return f"Błąd: {e}"