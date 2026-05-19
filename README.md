# AI Inbox Triage

A privacy-focused, local-first email categorization and triage tool. It automatically fetches unread emails via IMAP and analyzes them using a local Ollama server running Meta's Llama 3 model. 

Designed for local execution: **Zero API costs. No cloud processing.**

## Features
* **Local Execution:** Emails are processed entirely on your local machine.
* **Dynamic Language Support:** Generates structured triage reports in English or Polish via terminal flags.
* **Smart Categorization:** Classifies emails into Work, University, Finance, Newsletter, or Spam.
* **Urgency Triage:** Assigns priority levels (HIGH, MEDIUM, LOW) and suggests concrete next steps.
* **Clean Dependency Tree:** Lightweight, decoupled architecture ready for packaging.

## Privacy & Security
This application is built with privacy in mind. It processes emails locally on your hardware. No email content is transmitted to external AI APIs or third-party cloud services.

* **Account Security:** Users are entirely responsible for securing their own credentials and local environment. 
* **App Passwords:** **Never use your primary email password directly.** Always generate and use an App-Specific Password (e.g., via Google Account settings) for IMAP access.

## Prerequisites
* **Python:** 3.10 or higher
* **Ollama:** Installed and running locally (Download from [ollama.com](https://ollama.com))
* **Model:** Llama 3 pulled locally:
  ```bash
  ollama run llama3

```

## 🛠️ Setup & Installation

1. **Clone the repository** and navigate to the project root:
```bash
cd ai-inbox-triage

```


2. **Create and activate a virtual environment:**
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

```


3. **Install dependencies:**
```bash
pip install -r requirements.txt

```


4. **Configure Environment Variables:**
Create a `.env` file in the root directory. Add your IMAP credentials:
```env
EMAIL_ACCOUNT=your.email@gmail.com
EMAIL_PASSWORD=your_app_specific_password
IMAP_SERVER=imap.gmail.com

```

## Usage

Run the main script to process your inbox. Use the `--lang` flag to specify the report language (defaults to `en`):

```bash
python email_fetcher.py --lang pl

```

## ⚠️ Disclaimers

* **AI Limitations:** AI-generated classifications and action suggestions may be inaccurate. Users should always review important emails and actions manually.
* **Trademarks:** Llama 3 is a trademark of Meta Platforms, Inc. This project is independent and is not affiliated with, endorsed by, or sponsored by Meta or Google.

## Roadmap

* [ ] **Batch Processing:** Fetch and analyze large volumes of emails in small batches to stay within LLM context window limits.
* [ ] **SQLite Persistence Layer:** Store processed email IDs locally to avoid redundant analyses.
* [ ] **Interactive Actions:** Provide a UI/CLI option to directly archive, delete, or flag emails on the IMAP server.
* [ ] **Desktop GUI:** Package the application into a user-friendly desktop interface.
* [ ] **Standalone Installer:** Bundle everything into a single `.exe` file for end-users, with automated Ollama dependency checks.

## License

Distributed under the MIT License. See `LICENSE` for more information.
