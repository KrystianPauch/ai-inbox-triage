# AI Inbox Triage

An intelligent email filtering and summarization tool built with Python. It connects to a Gmail inbox via IMAP, extracts unread messages, and uses the Google Gemini AI model to categorize and summarize them, separating important emails from the noise.

## Features
* **Secure IMAP Connection:** Safely fetches emails without marking them as read using the `PEEK` command.
* **Content Extraction:** Automatically parses multipart emails to extract clean, plain text bodies while ignoring attachments.
* **AI-Powered Analysis:** Integrates with Google Gemini (1.5 Flash) to assign priorities, categorize content, and generate one-sentence summaries.
* **Bilingual CLI:** Command-line interface supports both English and Polish outputs.

## Tech Stack
* **Language:** Python 3
* **Libraries:** `imaplib`, `email`, `argparse`
* **AI Integration:** `google-generativeai` (Gemini API)
* **Environment Management:** `python-dotenv`

## Setup & Installation

1. **Clone the repository:**
```bash
git clone <your-repository-url>
cd ai_email_triage
```
2. **Set up a virtual environment (optional but recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```
3. **Install dependencies:**
```bash
pip install google-generativeai python-dotenv
```
4. **Environment Variables:**
Create a `.env` file in the root directory and add your credentials:
```text
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_app_password
GEMINI_API_KEY=your_google_ai_studio_key
```
## Usage

Run the script from the terminal. By default, it runs with the English UI.

**English UI:**
```bash
python email_fetcher.py
```
**Polish UI:**
```bash
python email_fetcher.py --lang pl
```

## 🚧 Known Issues & TODO
* **[Issue]:** Gemini API (Free Tier) blocks requests from the EU region, resulting in 429 and 404 errors.
* **[TODO]:** Migrate the AI engine to a fully local solution (Ollama). This will bypass regional restrictions, eliminate potential API costs, and ensure 100% privacy for email content.