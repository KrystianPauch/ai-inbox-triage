import imaplib

class EmailManager:
    def __init__(self, mail_connection, lang="en"):
        """Initializes the manager with an active IMAP connection and locale settings."""
        self.mail = mail_connection
        self.lang = lang

    def mark_as_read(self, email_id):
        """Applies the Seen flag to the specified email using strictly formatted IMAP lists."""
        try:
            self.mail.store(email_id, '+FLAGS', '(\\Seen)')
            clean_id = email_id.decode() if isinstance(email_id, bytes) else email_id
            return f"[{clean_id}] Oznaczono jako przeczytane." if self.lang == "pl" else f"[{clean_id}] Marked as read."
        except Exception as e:
            return f"Błąd: {e}" if self.lang == "pl" else f"Error: {e}"

    def move_to_folder(self, email_id, folder_name):
        """Moves an email safely using COPY and marking as Deleted."""
        try:
            clean_id = email_id.decode() if isinstance(email_id, bytes) else email_id
            
            if folder_name not in ["[Gmail]/Wszystkie", "[Gmail]/All Mail"]:
                self.mail.create(f'"{folder_name}"')
            
            self.mail.store(email_id, '+FLAGS', '(\\Seen)')
            
            if folder_name in ["[Gmail]/Wszystkie", "[Gmail]/All Mail"]:
                self.mail.store(email_id, '+FLAGS', '(\\Deleted)')
                return f"[{clean_id}] Zarchiwizowano w zakładce Wszystkie." if self.lang == "pl" else f"[{clean_id}] Archived."
            
            result, _ = self.mail.copy(email_id, f'"{folder_name}"')
            
            if result == 'OK':
                self.mail.store(email_id, '+FLAGS', '(\\Deleted)')
                return f"[{clean_id}] Przeniesiono do: {folder_name}" if self.lang == "pl" else f"[{clean_id}] Moved to: {folder_name}"
            else:
                return f"[{clean_id}] Błąd kopiowania." if self.lang == "pl" else f"[{clean_id}] Copy operation failed."
        except Exception as e:
            return f"Błąd operacji IMAP: {e}" if self.lang == "pl" else f"IMAP operation error: {e}"

    def archive_email(self, email_id, archive_folder=None):
        """Moves an email to the Archive folder."""
        if archive_folder is None:
            archive_folder = "[Gmail]/All Mail" if self.lang == "en" else "[Gmail]/Wszystkie"
        return self.move_to_folder(email_id, archive_folder)

    def trash_email(self, email_id, trash_folder=None):
        """Moves an email to the Trash folder."""
        if trash_folder is None:
            trash_folder = "[Gmail]/Trash" if self.lang == "en" else "[Gmail]/Kosz"
        return self.move_to_folder(email_id, trash_folder)

    def empty_trash(self, trash_folder=None):
        """Permanently deletes all emails in the specified Trash folder."""
        if trash_folder is None:
            trash_folder = "[Gmail]/Trash" if self.lang == "en" else "[Gmail]/Kosz"
            
        try:
            self.mail.select(f'"{trash_folder}"')
            
            status, response = self.mail.search(None, 'ALL')
            if status == 'OK':
                email_ids = response[0].split()
                for e_id in email_ids:
                    self.mail.store(e_id, '+FLAGS', '(\\Deleted)')
                self.mail.expunge()
                
            self.mail.select('INBOX')
            return "Kosz został trwale opróżniony." if self.lang == "pl" else "Trash emptied successfully."
        except Exception as e:
            return f"Błąd opróżniania kosza: {e}" if self.lang == "pl" else f"Error emptying trash: {e}"