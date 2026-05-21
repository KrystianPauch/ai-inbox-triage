# AI Inbox Triage

A privacy-focused, local-first email categorization and triage desktop application. It securely connects to your inbox via IMAP, allows server-side deep searching, and analyzes emails using a local Ollama server running Meta's Llama 3 model.

Designed for local execution: **Zero API costs. No cloud processing.**

## Features
* **Stateful Desktop GUI:** A modern, dark-themed graphical interface built with `CustomTkinter` that maintains persistent, secure IMAP sessions without triggering server lockouts.
* **Local AI Execution:** Emails are processed entirely on your local machine using Llama 3.
* **Server-Side Deep Search:** Utilizes the IMAP `TEXT` protocol to query and filter emails directly on the server before downloading payloads, significantly reducing memory footprint.
* **Strict IMAP Compliance:** Adheres strictly to RFC 3501 standards for flag management (e.g., `\Seen`, `\Deleted`), preventing inbox synchronization issues.
* **Dynamic Localization:** Switch seamlessly between English and Polish UI and AI prompts directly from the login screen.
* **Urgency Triage & Actions:** Classifies emails (Work, University, Finance, Newsletter, Spam), assigns priority levels, and allows one-click execution of IMAP actions (Trash, Archive, Mark as Read, Ignore).

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

## Setup & Installation

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
Ensure you have the required GUI and parsing libraries installed:

```bash
pip install -r requirements.txt
pip install customtkinter python-dotenv

```

4. **Configure Environment Variables:**
Create a `.env` file in the root directory. The application will auto-fill the login screen using these credentials.

```env
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_app_specific_password
IMAP_SERVER=imap.gmail.com

```

## Usage

Run the main application script to launch the GUI:

```bash
python app.py

```

*Authenticate via the login screen. You can select your preferred interface and AI reporting language before establishing the connection.*

## Architecture Overview

* `app.py`: Frontend application loop, GUI rendering, and stateful session management.
* `email_fetcher.py`: Core IMAP retrieval engine, payload parsing, and Deep Search logic.
* `email_manager.py`: Encapsulated server action handler (moves, flags, and deletions).
* `ai_analyzer.py`: Integration layer for local LLM text processing and prompt execution.

## Disclaimers

* **AI Limitations:** AI-generated classifications and action suggestions may be inaccurate. Users should always review important emails and actions manually.
* **Trademarks:** Llama 3 is a trademark of Meta Platforms, Inc. This project is independent and is not affiliated with, endorsed by, or sponsored by Meta or Google.

## Roadmap

* [x] **Desktop GUI:** Package the application into a user-friendly interface.
* [x] **Interactive Actions:** Provide direct IMAP operations (archive, trash, read) from the interface.
* [ ] **Batch Processing:** Fetch and analyze large volumes of emails in small batches to stay within LLM context window limits.
* [ ] **SQLite Persistence Layer:** Store processed email IDs locally to avoid redundant analyses.
* [ ] **Standalone Installer:** Bundle everything into a single `.exe` file for end-users, with automated Ollama dependency checks.

## License

Distributed under the MIT License. See `LICENSE` for more information.

```