# AutoTA Gmail Bot

AutoTA is a Gmail automation bot that:

* Reads unread Gmail messages.
* Uses OpenAI to generate human-like responses.
* Replies to the sender while maintaining conversation context.
* Stores conversation history and sender summaries in SQLite.
* Provides a Streamlit dashboard for monitoring and editing stored data.

---

## Features

* **Gmail API Integration** – Reads, sends, and marks emails as read.
* **AI-Powered Replies** – Uses OpenAI to generate natural, Markdown-formatted responses.
* **Sender Context Tracking** – Maintains a rolling summary for each sender.
* **Dashboard** – Built with Streamlit for viewing messages, editing summaries, and running the bot manually.

---

## Project Structure

```
.
├── get_refresh_token.py   # Script to generate Gmail OAuth token.json
├── bot/
│   ├── __init__.py
│   ├── config.py          # Loads environment variables and paths
│   ├── database.py        # SQLite wrapper for messages & senders
│   ├── gmail_client.py    # Gmail API client wrapper
│   ├── handler.py         # Main logic for handling each message
│   ├── main.py            # Entry point to run the bot
│   ├── message_parser.py  # Utility functions to parse emails
│   └── responder.py       # OpenAI-powered email response generator
└── dashboard/
    └── app.py             # Streamlit-based dashboard UI
```

---

## Requirements

* Python 3.9+
* Google Cloud project with Gmail API enabled
* OpenAI API key

### Python Libraries

Install dependencies with:

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```
google-auth-oauthlib
google-api-python-client
openai
python-dotenv
email-reply-parser
markdown2
streamlit
pandas
```

---

## Setup

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project and enable the **Gmail API**.
3. Create OAuth 2.0 credentials for a desktop app.
4. Note your `client_id` and `client_secret`.

### 2. Create `.env`

Create a `.env` file in the root directory:

```
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
OPENAI_API_KEY=your_openai_key
BASE_URL=http://localhost:8000
```

### 3. Get OAuth Token

Run the script to authenticate and generate `token.json`:

```bash
python get_refresh_token.py
```

This starts a local server on `http://localhost:8080` for the OAuth flow.

---

## Database

SQLite database located at `shared/data.db`. The schema is applied automatically on first run using `shared/schema.sql`.

---

## Running the Bot

Run the Gmail bot:

```bash
python -m bot.main
```

The bot will:

* Fetch unread messages
* Generate responses
* Reply to messages
* Mark them as read

---

## Dashboard

Launch the Streamlit dashboard:

```bash
streamlit run dashboard/app.py
```

### Dashboard Tabs

* **Messages** – Browse message history and view threads.
* **Senders** – View and manually edit sender summaries.
* **Bot Control** – Run the bot manually from the UI.

---

## Logs

The bot writes logs to `bot.log`.

---

## Notes

* For production, ensure `token.json` and `data.db` are secured.
* `BASE_URL` is used in email footers for feedback links.
