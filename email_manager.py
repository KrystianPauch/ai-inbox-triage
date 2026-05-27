import imaplib
import email
from email.header import decode_header
import email.utils
import re

class EmailManager:
    def __init__(self, mail_connection, lang="en"):

        self.mail = mail_connection
        self.lang = lang

    def archive_email(self, email_uid):

        self.mail.select("INBOX", readonly=False)

        archive_folders = ['"[Gmail]/Wszystkie"', '"[Gmail]/All Mail"']
        copied_successfully = False
        
        for folder in archive_folders:
            status, response = self.mail.uid('COPY', email_uid, folder)
            if status == 'OK':
                copied_successfully = True
                break

        if copied_successfully:
            self.mail.uid('STORE', email_uid, '+FLAGS', '\\Deleted')
            self.mail.expunge()
            return "Zarchiwizowano." if self.lang == "pl" else "Archived."
        else:
            return "Błąd archiwizacji." if self.lang == "pl" else "Archive error."

    def trash_email(self, email_uid):

        self.mail.select("INBOX", readonly=False)
 
        trash_folders = ['"[Gmail]/Kosz"', '"[Gmail]/Trash"', 'Trash', 'Kosz']
        copied_successfully = False
        
        for folder in trash_folders:
            status, response = self.mail.uid('COPY', email_uid, folder)
            if status == 'OK':
                copied_successfully = True
                break

        if copied_successfully:
            self.mail.uid('STORE', email_uid, '+FLAGS', '\\Deleted')
            self.mail.expunge()
            return "Przeniesiono do kosza." if self.lang == "pl" else "Moved to Trash."
        else:
            return "Błąd usuwania." if self.lang == "pl" else "Trash error."

    def mark_as_read(self, email_uid):

        self.mail.select("INBOX", readonly=False)
        self.mail.uid('STORE', email_uid, '+FLAGS', '\\Seen')

    def empty_trash(self, trash_folder=None):
        try:
            folders_to_try = ['"[Gmail]/Kosz"', '"[Gmail]/Trash"', 'Trash', 'Kosz']
            folder_selected = False
            
            for folder in folders_to_try:
                status, response = self.mail.select(folder)
                if status == 'OK':
                    folder_selected = True
                    break
            
            if not folder_selected:
                return "Błąd: Nie znaleziono folderu Kosz na serwerze." if self.lang == "pl" else "Error: Trash folder not found on server."

            status, response = self.mail.search(None, 'ALL')
            if status == 'OK' and response[0]:
                for e_id in response[0].split():
                    self.mail.store(e_id, '+FLAGS', '\\Deleted')
                self.mail.expunge()
            
            self.mail.select('INBOX')
            return "Kosz został trwale opróżniony." if self.lang == "pl" else "Trash emptied successfully."
        except Exception as e:
            return f"Błąd: {e}" if self.lang == "pl" else f"Error: {e}"
        
    def create_folder_action(self):
        if self.manager:
            folder_name = self.folder_entry.get().strip()
            if not folder_name:
                msg = "\n[System] Wpisz nazwę folderu w pole tekstowe!\n" if self.current_lang == "pl" else "\n[System] Enter folder name in the field!\n"
                self.textbox.insert("end", msg)
                return
            
            wynik = self.manager.create_folder(folder_name)
            self.textbox.insert("end", f"\n[System] {wynik}\n")

            obecne_wartosci = list(self.folder_entry.cget("values"))
            if folder_name not in obecne_wartosci:
                if obecne_wartosci == ["-"] or obecne_wartosci == ["INBOX"]:
                    obecne_wartosci = []
                obecne_wartosci.append(folder_name)
                self.folder_entry.configure(values=obecne_wartosci)
                self.folder_entry.set(folder_name)

    def move_email(self, email_uid, folder_name):
        try:
            self.mail.select("INBOX", readonly=False)
            formatted_name = f'"{folder_name}"' if ' ' in folder_name else folder_name
            
            status, response = self.mail.uid('COPY', email_uid, formatted_name)
            if status == 'OK':
                self.mail.uid('STORE', email_uid, '+FLAGS', '\\Deleted')
                self.mail.expunge()
                return "Przeniesiono" if self.lang == "pl" else "Moved"
            else:
                return "Błąd (sprawdź czy folder istnieje)" if self.lang == "pl" else "Error (check if folder exists)"
        except Exception as e:
            return f"Błąd: {e}"
        
    def get_folders(self):
        try:
            status, folders = self.mail.list()
            if status != 'OK' or not folders:
                return ["-"]
            
            folder_list = []
            for folder in folders:
                if isinstance(folder, tuple):
                    folder = folder[0]
                if not folder:
                    continue
                
                folder_str = folder.decode('utf-8', errors='ignore')
                
                if '"/"' in folder_str:
                    name = folder_str.split('"/"')[-1].strip(' "')
                elif ' "/" ' in folder_str:
                    name = folder_str.split(' "/" ')[-1].strip(' "')
                else:
                    name = folder_str.split()[-1].strip(' "')
                
                if name.startswith("[Gmail]") or name.upper() == "INBOX":
                    continue
                
                if name and name not in folder_list:
                    folder_list.append(name)
            
            return folder_list if folder_list else ["-"]
        except Exception:
            return ["-"]