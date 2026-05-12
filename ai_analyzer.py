import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from environment
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_emails(emails):
    """
    Sends email data to Gemini AI for triage and summarization.
    """
    if not emails:
        return "No emails to analyze."

    # Initialize the model (Gemini 1.5 Flash is fast and free)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Prepare the data for the prompt
    email_context = ""
    for idx, mail in enumerate(emails):
        email_context += f"\n--- Email #{idx+1} ---\n"
        email_context += f"From: {mail['sender']}\n"
        email_context += f"Subject: {mail['subject']}\n"
        email_context += f"Content: {mail['body'][:500]}\n" # Limit body for the prompt

    prompt = f"""
    You are an AI Email Assistant. Analyze the following emails and for each one:
    1. Give it a Priority (Low, Medium, High).
    2. Categorize it (e.g., Work, University, Spam, Social).
    3. Provide a 1-sentence summary in English.

    Emails to analyze:
    {email_context}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Analysis failed: {e}"