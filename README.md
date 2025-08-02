# AutoTA Gmail Bot

AutoTA (TaraBot) is a Gmail automation bot that:

* Reads unread Gmail messages.
* Uses OpenAI to generate human-like responses.
* Replies to the sender while maintaining conversation context.
* Stores conversation history and sender summaries in SQLite.
* Provides a Streamlit dashboard for monitoring and editing stored data.
* Includes a feedback endpoint for collecting quick thumbs up/down responses from email recipients.

---

## Features

* **Gmail API Integration** – Reads, sends, and marks emails as read.
* **AI-Powered Replies** – Uses OpenAI to generate natural, Markdown-formatted responses.
* **Sender Context Tracking** – Maintains a rolling summary for each sender.
* **Dashboard** – Built with Streamlit for viewing messages, editing summaries, running the bot manually, and managing RAG (retrieval augmented generation) documents.
* **Feedback Server** – A lightweight Flask endpoint (`/feedback`) that records vote responses and thanks the user with a friendly page.

---

## Project Structure

```
.
├── get_refresh_token.py     # Script to generate Gmail OAuth token.json
├── manage_users.py          # CLI for managing dashboard users
├── feedback/feedback_server.py  # Flask feedback endpoint
├── bot/
│   ├── __init__.py
│   ├── config.py            # Loads environment variables and paths
│   ├── database.py          # SQLite wrapper for messages, senders, votes, etc.
│   ├── embeddings.py        # Embedding utility for document chunks
│   ├── gmail_client.py      # Gmail API client wrapper
│   ├── handler.py           # Core message handling pipeline
│   ├── main.py              # Entry point to run the bot
│   ├── message_parser.py    # Email parsing helpers
│   ├── responder.py         # AI-powered response generation
│   └── search.py            # Semantic document search
└── dashboard/
    ├── app.py               # Streamlit dashboard UI
    └── helpers.py           # LaTeX-to-Markdown and text chunking
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

---

## Setup & Local Development

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
BASE_URL=http://localhost:5000
```

### 3. Get OAuth Token

Run:

```bash
python get_refresh_token.py
```

This authenticates and creates `token.json` for Gmail API access.

### 4. Initialize & Manage Users

```bash
python manage_users.py init
python manage_users.py add --username admin --password <your-password>
```

### 5. Run the Bot

```bash
python -m bot.main
```

### 6. Launch Dashboard

```bash
streamlit run dashboard/app.py
```

Then log in with your created username/password.

---

# Deployment on DigitalOcean

### 1. Python & Virtual Environment

```bash
sudo apt install python3.13-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Streamlit Dashboard (initially for testing)

```bash
streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port 8501
```

(If you're using the SSH extension with VSCode, then it should let you view it locally at this point using port forwarding.)

### 3. Add a User

```bash
python manage_users.py add --username admin --password <your-password>
```

### 4. Generate Gmail Token

```bash
python get_refresh_token.py
```

This creates `token.json` for Gmail API access.

### 5. Test the Bot

```bash
python -m bot.main
```

### 6. Install Caddy (reverse proxy & HTTPS)

```bash
sudo apt update
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
caddy version
```

### 7. Configure Caddy

Example `/etc/caddy/Caddyfile`:

```
your-subdomain.your-domain.tld {
    handle /feedback* {
        reverse_proxy localhost:5000
    }

    handle_path /* {
        reverse_proxy localhost:8501
    }
}
```

Reload Caddy:

```bash
sudo systemctl reload caddy
```

### 8. Visit the Website

* Dashboard: `https://your-subdomain.your-domain.tld`
* Feedback endpoint: `https://your-subdomain.your-domain.tld/feedback`

### 9. Run Apps in Background

Run both Streamlit and Flask servers as background services (e.g., `systemd`, `screen`, or `tmux`) so they restart automatically after droplet reboot.

### 10. Install Pandoc (required for LaTeX document uploads)

```bash
sudo apt install pandoc
```

---

## Deployment Notes

* Emails sent by the bot must reference the correct domain in URLs (as configured in the Caddyfile).
* Feedback server works automatically via reverse proxy.
* Consider adding `systemd` services for production stability.
* Make sure to add `your-subdomain.your-domain.tld` as `BASE_URL` environment variable.

---

## Logs

Bot logs are stored in `bot.log`.

---

## Security Notes

* Uses username/password authentication for dashboard.
* Gmail OAuth tokens (`token.json`) and database (`data.db`) should be kept secure.
* HTTPS is provided automatically by Caddy when using a domain name.

---

## Future Improvements

* Systemd unit files for automatic startup.
* Email templates for better branding.
* Optionally integrate multiple apps under different subdomains using Caddy.
