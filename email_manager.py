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

    def archive_email(self, email_id):
        self.mail.select("INBOX", readonly=False)
        folder = '"[Gmail]/All Mail"' if self.lang == "en" else '"[Gmail]/Wszystkie"'
        self.mail.copy(email_id, folder)
        self.mail.store(email_id, '+FLAGS', '\\Deleted')

    def trash_email(self, email_id):
        self.mail.select("INBOX", readonly=False)
        folder = '"[Gmail]/Trash"' if self.lang == "en" else '"[Gmail]/Kosz"'
        self.mail.copy(email_id, folder)
        self.mail.store(email_id, '+FLAGS', '\\Deleted')

    def mark_as_read(self, email_id):
        typ, _ = self.mail.select("INBOX", readonly=False)
        print(f"\n[IMAP] Stan otwarcia INBOX: {typ}")
        
        typ_seq, data_seq = self.mail.store(email_id, '+FLAGS', '\\Seen')
        print(f"[IMAP] Odpowiedź dla Sekwencyjnego ID: {typ_seq} | Dane: {data_seq}")
        
        typ_uid, data_uid = self.mail.uid('STORE', email_id, '+FLAGS', '\\Seen')
        print(f"[IMAP] Odpowiedź dla Unikalnego UID: {typ_uid} | Dane: {data_uid}")

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
        
    def process_action(self, action):
        if not self.emails_cache or self.current_email_index >= len(self.emails_cache):
            return

        email_id = self.emails_cache[self.current_email_index].get('id')

        if self.manager and action != "ignore":
            try:
                if action == "trash":
                    self.manager.trash_email(email_id)
                elif action == "archive":
                    self.manager.archive_email(email_id)
                elif action == "read":
                    self.manager.mark_as_read(email_id)
            except Exception as e:
                self.textbox.insert("end", f"\n[IMAP Error] {e}\n")
                return

        self.current_email_index += 1
        self.display_current_email()