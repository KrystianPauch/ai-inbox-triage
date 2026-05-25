import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def analyze_emails(email_data, lang="pl"):
    if not email_data:
        return "Brak danych." if lang == "pl" else "No data."

    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama" 
    )

    email_context = f"Od: {email_data.get('sender', '')}\n"
    email_context += f"Data: {email_data.get('date', '')}\n"
    email_context += f"Temat: {email_data.get('subject', '')}\n"
    email_context += f"Treść: {email_data.get('body', '')[:500]}\n"

    if lang == "pl":
        prompt = f"""Jesteś zaawansowanym asystentem AI ds. zarządzania pocztą. 
Twoim zadaniem jest analiza e-maili. MUSISZ ODPOWIADAĆ WYŁĄCZNIE W JĘZYKU POLSKIM. Zignoruj inne języki.
ZABRONIONE JEST używanie jakichkolwiek wstępów. Zwróć od razu sam wynik w wymaganym formacie.

Dla wiadomości zwróć ściśle poniższy format:
- [AUTOR]: (Imię, nazwisko lub nazwa firmy) (podaj pełny adres e-mail w nawiasach)
- [DATA]: (Przepisz dokładnie datę i godzinę podaną w kontekście wiadomości)
- [TEMAT]: (Oryginalny temat wiadomości)
- [PRIORYTET]: WYSOKI, ŚREDNI lub NISKI.
- [KATEGORIA]: (Praca, Uczelnia, Finanse, Newsletter lub Spam).
- [PODSUMOWANIE]: Dokładnie jedno zdanie po polsku.
- [AKCJA]: Krótka porada (np. 'Odpisz dzisiaj', 'Archiwizuj', 'Zignoruj').

Wiadomość:
{email_context}"""
    else:
        prompt = f"""You are an elite AI Email Triage Specialist. Analyze the email.
DO NOT include any conversational filler. Output strictly the requested format immediately.

For the email, provide the following fields in English:
- [SENDER]: (Name or company) (include full email address in parentheses)
- [DATE]: (Copy exactly the date and time provided in the email context)
- [SUBJECT]: (Original email subject)
- [PRIORITY]: HIGH, MEDIUM, or LOW.
- [CATEGORY]: (Work, University, Finance, Newsletter, or Spam).
- [SUMMARY]: A concise, one-sentence summary.
- [ACTION]: Suggest a quick next step.

Email:
{email_context}"""

    try:
        response = client.chat.completions.create(
            model="llama3",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2 
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"