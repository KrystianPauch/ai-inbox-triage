import imaplib

class EmailManager:
    def __init__(self, mail_connection, lang="en"):
        """Initializes the manager with an active IMAP connection and locale settings."""
        self.mail = mail_connection
        self.lang = lang

    def mark_as_read(self, email_id):
        """Applies the \Seen flag to the specified email."""
        try:
            self.mail.store(email_id, '+FLAGS', '\\Seen')
            return f"[{email_id}] Oznaczono jako przeczytane." if self.lang == "pl" else f"[{email_id}] Marked as read."
        except Exception as e:
            return f"Błąd: {e}" if self.lang == "pl" else f"Error: {e}"

    def move_to_folder(self, email_id, folder_name):
        """Moves an email to a specified folder via IMAP COPY and EXPUNGE commands."""
        try:
            # Ensure the target folder exists (ignores if already created)
            self.mail.create(f'"{folder_name}"')
            
            # Execute copy-and-delete sequence for moving
            result, _ = self.mail.copy(email_id, f'"{folder_name}"')
            
            if result == 'OK':
                self.mail.store(email_id, '+FLAGS', '\\Deleted')
                return f"[{email_id}] Przeniesiono do: {folder_name}" if self.lang == "pl" else f"[{email_id}] Moved to: {folder_name}"
            else:
                return f"[{email_id}] Błąd kopiowania." if self.lang == "pl" else f"[{email_id}] Copy operation failed."
        except Exception as e:
            return f"Błąd operacji IMAP: {e}" if self.lang == "pl" else f"IMAP operation error: {e}"

    def archive_email(self, email_id, archive_folder="Archive"):
        """Moves an email to the Archive folder."""
        return self.move_to_folder(email_id, archive_folder)

    def trash_email(self, email_id, trash_folder="Trash"):
        """Moves an email to the Trash folder."""
        return self.move_to_folder(email_id, trash_folder)

    def empty_trash(self, trash_folder="Trash"):
        """Permanently deletes all emails in the specified Trash folder."""
        try:
            self.mail.select(f'"{trash_folder}"')
            self.mail.expunge()
            # Return to INBOX so we don't break the main loop
            self.mail.select('INBOX')
            return "Kosz opróżniony." if self.lang == "pl" else "Trash emptied successfully."
        except Exception as e:
            return f"Błąd opróżniania kosza: {e}" if self.lang == "pl" else f"Error emptying trash: {e}"