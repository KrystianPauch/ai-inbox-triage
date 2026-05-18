import os
from google import genai
from dotenv import load_dotenv

# Load API key from environment
load_dotenv()

def analyze_emails(emails):
    """
    Sends email data to Gemini AI for triage and summarization.
    """
    if not emails:
        return "No emails to analyze."

    # Initialize the new GenAI client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # Prepare the data for the prompt
    email_context = ""
    for idx, mail in enumerate(emails):
        email_context += f"\n--- Email #{idx+1} ---\n"
        email_context += f"From: {mail['sender']}\n"
        email_context += f"Subject: {mail['subject']}\n"
        email_context += f"Content: {mail['body'][:500]}\n" # Limit body for the prompt

    prompt = f"""
    You are an elite AI Email Triage Specialist. Analyze the following emails.
    For each email, provide the following fields in a clear, structured way:
    - [PRIORITY]: HIGH, MEDIUM, or LOW (High only if action is needed urgently).
    - [CATEGORY]: (Work, University, Finance, Newsletter, or Spam).
    - [SUMMARY]: A concise, one-sentence summary in English.
    - [ACTION]: Suggest a quick next step (e.g., 'Reply today', 'Archive', 'Ignore').

    Emails:
    {email_context}
    """

    try:
        # New generate_content syntax
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI Analysis failed: {e}"