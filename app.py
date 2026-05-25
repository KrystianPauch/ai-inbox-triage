import os
import customtkinter as ctk
import imaplib
import threading
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
        self.geometry("800x600")
        
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
        """Builds the login screen interface."""
        load_dotenv()
        
        self.login_frame.pack(expand=True, fill="both", padx=50, pady=50)

        ctk.CTkLabel(self.login_frame, text="Logowanie IMAP", font=("Arial", 24, "bold")).pack(pady=(40, 20))

        self.email_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Adres Email", width=300)
        self.email_entry.pack(pady=10)
        if os.getenv('EMAIL_ADDRESS'):
            self.email_entry.insert(0, os.getenv('EMAIL_ADDRESS'))

        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Hasło App Password", show="*", width=300)
        self.password_entry.pack(pady=10)
        if os.getenv('EMAIL_PASSWORD'):
            self.password_entry.insert(0, os.getenv('EMAIL_PASSWORD'))

        self.lang_var = ctk.StringVar(value="pl")
        self.lang_menu = ctk.CTkOptionMenu(self.login_frame, values=["pl", "en"], variable=self.lang_var, width=300)
        self.lang_menu.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.login_frame, text="", text_color="red")
        self.status_label.pack(pady=5)

        self.login_btn = ctk.CTkButton(self.login_frame, text="Zaloguj", command=self.perform_login, width=300)
        self.login_btn.pack(pady=20)

    def build_main_screen(self):
        """Builds the interface of the main application panel."""
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

        self.bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.bottom_frame.grid(row=2, column=0, padx=0, pady=10, sticky="ew")

        self.btn_trash = ctk.CTkButton(self.bottom_frame, text="Kosz", fg_color="#8B0000", hover_color="#333333", command=lambda: self.process_action("trash"))
        self.btn_trash.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_archive = ctk.CTkButton(self.bottom_frame, text="Archiwum", fg_color="#555555", hover_color="#333333", command=lambda: self.process_action("archive"))
        self.btn_archive.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_read = ctk.CTkButton(self.bottom_frame, text="Przeczytane", fg_color="#006400", hover_color="#333333", command=lambda: self.process_action("read"))
        self.btn_read.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_ignore = ctk.CTkButton(self.bottom_frame, text="Zignoruj", fg_color="transparent", hover_color="#333333", border_width=1, command=lambda: self.process_action("ignore"))
        self.btn_ignore.pack(side="left", padx=(5, 10), expand=True, fill="x")

    def show_login_screen(self):
        self.main_frame.pack_forget()
        self.login_frame.pack(expand=True, fill="both")

    def show_main_screen(self):
        """Switches the view to the main panel and updates the texts depending on the language."""
        self.login_frame.pack_forget()
        self.main_frame.pack(expand=True, fill="both")
        
        if self.current_lang == "en":
            self.fetch_btn.configure(text="Fetch & Analyze")
            self.logout_btn.configure(text="Logout")
            self.btn_trash.configure(text="Trash")
            self.btn_archive.configure(text="Archive")
            self.btn_read.configure(text="Mark as Read")
            self.btn_ignore.configure(text="Ignore")
        else:
            self.fetch_btn.configure(text="Pobierz i Analizuj")
            self.logout_btn.configure(text="Wyloguj")
            self.btn_trash.configure(text="Kosz")
            self.btn_archive.configure(text="Archiwum")
            self.btn_read.configure(text="Przeczytane")
            self.btn_ignore.configure(text="Zignoruj")

    def perform_login(self):
        """Establishes a permanent connection to the server and goes to the main screen."""
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        self.current_lang = self.lang_var.get()

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
            if self.manager:
                try:
                    self.manager.mail.select("INBOX", readonly=False)
                    self.manager.mail.expunge()
                except:
                    pass

            fetched_data, _ = check_inbox(language=self.current_lang, limit=3, mode='all')
            
            for email in fetched_data:
                try:
                    report_text = analyze_emails(email, self.current_lang)
                    email['ai_report'] = str(report_text)
                except Exception as ai_err:
                    email['ai_report'] = f"[Llama 3 Error: {ai_err}]"
            
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
        
        self.textbox.insert("end", f"Od: {sender}\nTemat: {subject}\n")
        self.textbox.insert("end", "-"*50 + "\n")
        self.textbox.insert("end", f"{ai_report}\n")
        self.textbox.insert("end", "="*50 + "\n")

    def process_action(self, action):
        if not self.emails_cache or self.current_email_index >= len(self.emails_cache):
            return

        email_data = self.emails_cache[self.current_email_index]
        email_id = email_data.get('id')
        
        print(f"\n[DEBUG] Action: {action.upper()}")
        print(f"[DEBUG] Raw email_id from cache: {email_id} (Type: {type(email_id)})")

        if self.manager and action != "ignore":
            try:
                if action == "trash":
                    self.manager.trash_email(email_id)
                elif action == "archive":
                    self.manager.archive_email(email_id)
                elif action == "read":
                    self.manager.mark_as_read(email_id)
                print("[DEBUG] IMAP command completed without python exceptions.")
            except Exception as e:
                print(f"[DEBUG] IMAP command failed with exception: {e}")
                self.textbox.insert("end", f"\n[Error] {e}\n")
                return

        self.current_email_index += 1
        self.display_current_email()

    def perform_logout(self):
        """Safely closes the session and returns to the login screen."""
        if self.manager:
            try:
                self.manager.mail.logout()
            except:
                pass
            self.manager = None
        self.textbox.delete("1.0", "end")
        self.show_login_screen()

    def on_closing(self):
        """Ensures that when the window is closed, the IMAP session does not hang on the server."""
        self.perform_logout()
        self.destroy()

if __name__ == "__main__":
    app = EmailTriageApp()
    app.mainloop()