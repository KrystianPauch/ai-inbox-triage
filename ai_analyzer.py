import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def analyze_emails(emails, lang="pl"):
    """
    Wysyła dane do lokalnej Ollamy z dynamicznym wyborem języka.
    """
    if not emails:
        return "Brak wiadomości do analizy." if lang == "pl" else "No emails to analyze."

    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama" 
    )

    email_context = ""
    for idx, mail in enumerate(emails):
        email_context += f"\n--- Email #{idx+1} ---\n"
        email_context += f"Od: {mail['sender']}\n"
        email_context += f"Temat: {mail['subject']}\n"
        email_context += f"Treść: {mail['body'][:500]}\n"


    if lang == "pl":
        prompt = f"""Jesteś zaawansowanym asystentem AI ds. zarządzania pocztą. 
Twoim zadaniem jest analiza e-maili. MUSISZ ODPOWIADAĆ WYŁĄCZNIE W JĘZYKU POLSKIM. Zignoruj inne języki.
ZABRONIONE JEST używanie jakichkolwiek wstępów typu "Here is the analysis", "Oto analiza", itp. Zwróć od razu sam wynik w wymaganym formacie.

Dla każdej wiadomości zwróć ściśle poniższy format:
- [AUTOR]: (Imię, nazwisko lub nazwa firmy) (podaj pełny adres e-mail w nawiasach)
- [TEMAT]: (Oryginalny temat wiadomości)
- [PRIORYTET]: WYSOKI, ŚREDNI lub NISKI.
- [KATEGORIA]: (Praca, Uczelnia, Finanse, Newsletter lub Spam).
- [PODSUMOWANIE]: Dokładnie jedno zdanie po polsku.
- [AKCJA]: Krótka porada (np. 'Odpisz dzisiaj', 'Archiwizuj', 'Zignoruj').

Wiadomości:
{email_context}"""
    else:
        prompt = f"""You are an elite AI Email Triage Specialist. Analyze the following emails.
DO NOT include any conversational filler like 'Here is the analysis...'. Output strictly the requested format immediately.

For each email, provide the following fields in English:
- [SENDER]: (Name or company) (include full email address in parentheses)
- [SUBJECT]: (Original email subject)
- [PRIORITY]: HIGH, MEDIUM, or LOW.
- [CATEGORY]: (Work, University, Finance, Newsletter, or Spam).
- [SUMMARY]: A concise, one-sentence summary.
- [ACTION]: Suggest a quick next step.

Emails:
{email_context}"""

    try:
        response = client.chat.completions.create(
            model="llama3",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2 
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Błąd analizy AI: {e}" if lang == "pl" else f"AI Analysis failed: {e}"