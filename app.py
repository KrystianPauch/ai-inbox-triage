import os
import customtkinter as ctk
import imaplib
import threading
import re
from dotenv import load_dotenv
from email_manager import EmailManager
from email_fetcher import check_inbox
from ai_analyzer import analyze_emails

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class EmailTriageApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Inbox Triage")
        self.geometry("850x600")
        
        self.manager = None
        self.current_lang = "pl"
        self.imap_server = 'imap.gmail.com'
        self.emails_cache = []
        self.current_email_index = 0

        self.login_frame = ctk.CTkFrame(self)
        self.main_frame = ctk.CTkFrame(self)

        self.build_login_screen()
        self.build_main_screen()
        self.show_login_screen()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def build_login_screen(self):
        load_dotenv()
        self.login_frame.pack(expand=True, fill="both", padx=50, pady=50)

        self.title_label = ctk.CTkLabel(self.login_frame, text="Connect to Gmail", font=("Arial", 24, "bold"))
        self.title_label.pack(pady=(40, 20))

        self.email_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Email Address", width=300)
        self.email_entry.pack(pady=10)
        if os.getenv('EMAIL_ADDRESS'):
            self.email_entry.insert(0, os.getenv('EMAIL_ADDRESS'))

        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="App Password", show="*", width=300)
        self.password_entry.pack(pady=10)
        if os.getenv('EMAIL_PASSWORD'):
            self.password_entry.insert(0, os.getenv('EMAIL_PASSWORD'))

        self.lang_var = ctk.StringVar(value="English")
        self.lang_menu = ctk.CTkOptionMenu(
            self.login_frame, 
            values=["English", "Polski"], 
            variable=self.lang_var, 
            width=300,
            command=self.change_login_language
        )
        self.lang_menu.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.login_frame, text="", text_color="red")
        self.status_label.pack(pady=5)

        self.login_btn = ctk.CTkButton(self.login_frame, text="Start", command=self.perform_login, width=300)
        self.login_btn.pack(pady=20)

    def change_login_language(self, choice):
        if choice == "English":
            self.title_label.configure(text="Connect to Gmail")
            self.email_entry.configure(placeholder_text="Email Address")
            self.password_entry.configure(placeholder_text="App Password")
            self.login_btn.configure(text="Start")
        else:
            self.title_label.configure(text="Połącz z pocztą Gmail")
            self.email_entry.configure(placeholder_text="Adres Email")
            self.password_entry.configure(placeholder_text="Hasło aplikacji")
            self.login_btn.configure(text="Rozpocznij")

    def build_main_screen(self):
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        top_frame = ctk.CTkFrame(self.main_frame)
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.fetch_btn = ctk.CTkButton(top_frame, text="Pobierz i Analizuj", command=self.fetch_emails)
        self.fetch_btn.pack(side="left", padx=10, pady=10)

        self.logout_btn = ctk.CTkButton(top_frame, text="Wyloguj", fg_color="#8B0000", hover_color="#550000", command=self.perform_logout)
        self.logout_btn.pack(side="right", padx=10, pady=10)

        self.textbox = ctk.CTkTextbox(self.main_frame, font=("Consolas", 13), wrap="word")
        self.textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        self.folder_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.folder_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.folder_entry = ctk.CTkComboBox(self.folder_frame, values=["-"], width=200)
        self.folder_entry.pack(side="left", padx=5)

        self.btn_new_folder = ctk.CTkButton(self.folder_frame, text="Stwórz folder", fg_color="#4A4A4A", hover_color="#333333", command=self.create_folder_action)
        self.btn_new_folder.pack(side="left", padx=5)

        self.btn_assign_folder = ctk.CTkButton(self.folder_frame, text="Przypisz mail", command=self.assign_to_folder_action)
        self.btn_assign_folder.pack(side="left", padx=5)

        self.bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.bottom_frame.grid(row=3, column=0, padx=0, pady=10, sticky="ew")

        self.btn_trash = ctk.CTkButton(self.bottom_frame, text="Kosz", fg_color="#8B0000", hover_color="#333333", command=lambda: self.process_action("trash"))
        self.btn_trash.pack(side="left", padx=3, expand=True, fill="x")

        self.btn_archive = ctk.CTkButton(self.bottom_frame, text="Archiwum", fg_color="#555555", hover_color="#333333", command=lambda: self.process_action("archive"))
        self.btn_archive.pack(side="left", padx=3, expand=True, fill="x")

        self.btn_read = ctk.CTkButton(self.bottom_frame, text="Przeczytane", fg_color="#006400", hover_color="#333333", command=lambda: self.process_action("read"))
        self.btn_read.pack(side="left", padx=3, expand=True, fill="x")

        self.btn_ignore = ctk.CTkButton(self.bottom_frame, text="Zignoruj", fg_color="#222222", hover_color="#333333", border_width=1, command=lambda: self.process_action("ignore"))
        self.btn_ignore.pack(side="left", padx=3, expand=True, fill="x")

        self.btn_prev = ctk.CTkButton(self.bottom_frame, text="⬅ Poprzednia", fg_color="transparent", hover_color="#333333", border_width=1, command=self.prev_email)
        self.btn_prev.pack(side="left", padx=3, expand=True, fill="x")

        self.btn_next = ctk.CTkButton(self.bottom_frame, text="Następna ➔", fg_color="transparent", hover_color="#333333", border_width=1, command=self.next_email)
        self.btn_next.pack(side="left", padx=(3, 10), expand=True, fill="x")

        self.empty_trash_btn = ctk.CTkButton(top_frame, text="Opróżnij Kosz", fg_color="#8B0000", hover_color="#550000", command=self.empty_trash_action)
        self.empty_trash_btn.pack(side="right", padx=10, pady=10)

    def show_login_screen(self):
        self.main_frame.pack_forget()
        self.login_frame.pack(expand=True, fill="both")

    def show_main_screen(self):
        self.login_frame.pack_forget()
        self.main_frame.pack(expand=True, fill="both")
        
        if self.current_lang == "en":
            self.fetch_btn.configure(text="Fetch & Analyze")
            self.logout_btn.configure(text="Logout")
            self.btn_trash.configure(text="Trash")
            self.btn_archive.configure(text="Archive")
            self.btn_read.configure(text="Mark as Read")
            self.btn_ignore.configure(text="Ignore")
            self.btn_prev.configure(text="⬅ Previous")
            self.btn_next.configure(text="Next ➔")
            self.empty_trash_btn.configure(text="Empty Trash")
            self.folder_entry.set("Folder name...")
            self.btn_new_folder.configure(text="Create folder")
            self.btn_assign_folder.configure(text="Assign email")
        else:
            self.fetch_btn.configure(text="Pobierz i Analizuj")
            self.logout_btn.configure(text="Wyloguj")
            self.btn_trash.configure(text="Kosz")
            self.btn_archive.configure(text="Archiwum")
            self.btn_read.configure(text="Przeczytane")
            self.btn_ignore.configure(text="Zignoruj")
            self.btn_prev.configure(text="⬅ Poprzednia")
            self.btn_next.configure(text="Następna ➔")
            self.empty_trash_btn.configure(text="Opróżnij Kosz")
            self.folder_entry.set("Nazwa folderu...")
            self.btn_new_folder.configure(text="Stwórz folder")
            self.btn_assign_folder.configure(text="Przypisz mail")

    def perform_login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        wybrany_jezyk = self.lang_var.get()
        self.current_lang = "pl" if wybrany_jezyk == "Polski" else "en"

        if not email or not password:
            self.status_label.configure(text="Wpisz email i hasło!" if self.current_lang == "pl" else "Enter email and password!")
            return

        self.status_label.configure(text="Łączenie..." if self.current_lang == "pl" else "Connecting...", text_color="yellow")
        self.update_idletasks()

        try:
            mail_conn = imaplib.IMAP4_SSL(self.imap_server)
            mail_conn.login(email, password)
            self.manager = EmailManager(mail_conn, lang=self.current_lang)
            self.status_label.configure(text="")
            self.show_main_screen()
            self.textbox.insert("end", f"[System] Zalogowano poprawnie jako: {email}\n" if self.current_lang == "pl" else f"[System] Logged in successfully as: {email}\n")
        except Exception as e:
            err_msg = f"Błąd: {e}" if self.current_lang == "pl" else f"Error: {e}"
            self.status_label.configure(text=err_msg, text_color="red")

    def fetch_emails(self):
        self.fetch_btn.configure(state="disabled")
        self.textbox.delete("1.0", "end")
        msg = "Pobieranie i analiza AI w toku...\n" if self.current_lang == "pl" else "Fetching & AI analysis in progress...\n"
        self.textbox.insert("end", f"[System] {msg}")
        
        thread = threading.Thread(target=self._fetch_emails_thread)
        thread.daemon = True
        thread.start()

    def _fetch_emails_thread(self):
        try:
            fetched_data, _ = check_inbox(self.manager.mail, language=self.current_lang, limit=5, mode='all')

            if self.manager and fetched_data:
                self.manager.mail.select("INBOX", readonly=False)
                for email_item in fetched_data:
                    seq_id = email_item.get('id')
                    if seq_id:
                        # Przetwarzanie ID niezależnie od typu (bytes/str)
                        raw_id = seq_id.decode('utf-8') if isinstance(seq_id, bytes) else str(seq_id)
                        res, data = self.manager.mail.fetch(raw_id, '(UID)')
                        if res == 'OK' and data[0]:
                            uid_match = re.search(r'UID\s+(\d+)', data[0].decode('utf-8', errors='ignore'))
                            if uid_match:
                                email_item['email_uid'] = uid_match.group(1)

            for email_item in fetched_data:
                try:
                    report_text = analyze_emails(email_item, self.current_lang)
                    email_item['ai_report'] = str(report_text)
                except Exception as ai_err:
                    email_item['ai_report'] = f"[Llama 3 Error: {ai_err}]"
            
            self.emails_cache = fetched_data
            self.current_email_index = 0
            self.after(0, self._update_ui_after_fetch)
        except Exception as e:
            err_msg = f"{e}\n"
            self.after(0, lambda: self.textbox.insert("end", f"[Error] {err_msg}"))
            self.after(0, lambda: self.fetch_btn.configure(state="normal"))

    def _update_ui_after_fetch(self):
        self.fetch_btn.configure(state="normal")
        msg = f"Zakończono. Znaleziono: {len(self.emails_cache)} wiadomości.\n" if self.current_lang == "pl" else f"Done. Found: {len(self.emails_cache)} messages.\n"
        self.textbox.insert("end", f"[System] {msg}")

        if self.manager:
            katalogi = self.manager.get_folders()
            if katalogi:
                self.folder_entry.configure(values=katalogi)
                self.folder_entry.set(katalogi[0])
            else:
                blad = "Błąd pobierania" if self.current_lang == "pl" else "Fetch error"
                self.folder_entry.configure(values=[blad])
                self.folder_entry.set(blad)
                
        if self.emails_cache:
            self.display_current_email()

    def display_current_email(self):
        self.textbox.delete("1.0", "end")
        if not self.emails_cache or self.current_email_index >= len(self.emails_cache):
            msg = "Brak wiadomości." if self.current_lang == "pl" else "No messages."
            self.textbox.insert("end", f"\n=== {msg} ===\n")
            return

        email_data = self.emails_cache[self.current_email_index]
        msg = f"Wiadomość {self.current_email_index + 1} / {len(self.emails_cache)}\n" if self.current_lang == "pl" else f"Message {self.current_email_index + 1} / {len(self.emails_cache)}\n"
        self.textbox.insert("end", msg)
        self.textbox.insert("end", "="*50 + "\n")
        
        sender = email_data.get('sender', 'Unknown')
        subject = email_data.get('subject', 'No Subject')
        ai_report = email_data.get('ai_report', '[Błąd analizy AI]')
        
        if self.current_lang == "en":
            self.textbox.insert("end", f"From: {sender}\nSubject: {subject}\n")
        else:
            self.textbox.insert("end", f"Od: {sender}\nTemat: {subject}\n")
            
        self.textbox.insert("end", "-"*50 + "\n")
        
        status = email_data.get('ui_status')
        if status:
            naglowek_statusu = "STATUS AKCJI" if self.current_lang == "pl" else "ACTION STATUS"
            self.textbox.insert("end", f">>> {naglowek_statusu}: {status} <<<\n")
            self.textbox.insert("end", "-"*50 + "\n")

        self.textbox.insert("end", f"{ai_report}\n")
        self.textbox.insert("end", "="*50 + "\n")

    def process_action(self, action):
        if not self.emails_cache or self.current_email_index >= len(self.emails_cache):
            return

        email_data = self.emails_cache[self.current_email_index]
        email_uid = email_data.get('email_uid')

        if not email_uid and action != "ignore":
            self.textbox.insert("end", "\n[Error] Brak przypisanego identyfikatora UID dla tej wiadomości.\n")
            return

        if email_data.get('ui_status') in ["Przeniesiono do kosza 🗑️", "Moved to Trash 🗑️", "Zarchiwizowano 📁", "Archived 📁"]:
            return

        if action == "ignore":
            email_data['ui_status'] = "Zignorowano 📝" if self.current_lang == "pl" else "Ignored 📝"
            self.display_current_email()
            return

        if self.manager:
            try:
                if action == "trash":
                    self.manager.trash_email(email_uid)
                    email_data['ui_status'] = "Przeniesiono do kosza 🗑️" if self.current_lang == "pl" else "Moved to Trash 🗑️"
                elif action == "archive":
                    self.manager.archive_email(email_uid)
                    email_data['ui_status'] = "Zarchiwizowano 📁" if self.current_lang == "pl" else "Archived 📁"
                elif action == "read":
                    self.manager.mark_as_read(email_uid)
                    email_data['ui_status'] = "Oznaczono jako przeczytane 👁️" if self.current_lang == "pl" else "Marked as Read 👁️"
                
                self.display_current_email()
            except Exception as e:
                self.textbox.insert("end", f"\n[Error] {e}\n")

    def next_email(self):
        if self.emails_cache:
            if self.current_email_index < len(self.emails_cache) - 1:
                self.current_email_index += 1
                self.display_current_email()
            else:
                self.fetch_emails()

    def prev_email(self):
        if self.emails_cache and self.current_email_index > 0:
            self.current_email_index -= 1
            self.display_current_email()

    def empty_trash_action(self):
        if self.manager:
            msg = "Trwa opróżnianie kosza na serwerze...\n" if self.current_lang == "pl" else "Emptying trash on server...\n"
            self.textbox.insert("end", f"\n[System] {msg}")
            self.update_idletasks()
            
            wynik = self.manager.empty_trash()
            self.textbox.insert("end", f"[System] {wynik}\n")

    def create_folder_action(self):
        if self.manager:
            folder_name = self.folder_entry.get().strip()
            if not folder_name:
                msg = "\n[System] Wpisz nazwę folderu w pole tekstowe!\n" if self.current_lang == "pl" else "\n[System] Enter folder name in the field!\n"
                self.textbox.insert("end", msg)
                return
            
            wynik = self.manager.create_folder(folder_name)
            self.textbox.insert("end", f"\n[System] {wynik}\n")

    def assign_to_folder_action(self):
        if not self.emails_cache or self.current_email_index >= len(self.emails_cache):
            return

        folder_name = self.folder_entry.get().strip()
        if not folder_name:
            msg = "\n[System] Wpisz nazwę folderu docelowego!\n" if self.current_lang == "pl" else "\n[System] Enter target folder name!\n"
            self.textbox.insert("end", msg)
            return

        email_data = self.emails_cache[self.current_email_index]
        email_uid = email_data.get('email_uid')

        if not email_uid:
            self.textbox.insert("end", "\n[Error] Brak przypisanego identyfikatora UID.\n" if self.current_lang == "pl" else "\n[Error] No UID assigned.\n")
            return

        if self.manager:
            try:
                status_text = self.manager.move_email(email_uid, folder_name)
                email_data['ui_status'] = f"{status_text} -> {folder_name} 📁"
                self.display_current_email()
            except Exception as e:
                self.textbox.insert("end", f"\n[Error] {e}\n")

    def perform_logout(self):
        if self.manager:
            try: self.manager.mail.logout()
            except: pass
            self.manager = None
        self.textbox.delete("1.0", "end")
        self.show_login_screen()

    def on_closing(self):
        self.perform_logout()
        self.destroy()

if __name__ == "__main__":
    app = EmailTriageApp()
    app.mainloop()