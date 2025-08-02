#!/usr/bin/env bash

set -e

echo "=== AutoTA Gmail Bot Setup ==="

# --- Check for Gmail token.json ---
if [ ! -f "token.json" ]; then
    echo "ERROR: token.json not found."
    echo "Please generate token.json locally using get_refresh_token.py and copy it to this server."
    echo "See the setup guide for details."
    exit 1
fi

# --- Ensure Python venv is available ---
if ! dpkg -s python3.13-venv >/dev/null 2>&1; then
    echo "Installing python3.13-venv..."
    sudo apt update
    sudo apt install -y python3.13-venv
fi

# --- Install Pandoc early ---
if ! command -v pandoc >/dev/null 2>&1; then
    echo "Pandoc not found. Installing..."
    sudo apt update
    sudo apt install -y pandoc
else
    echo "Pandoc is already installed."
fi

# --- Create virtual environment if missing ---
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    apt install python3.12-venv
    python3 -m venv .venv
fi

# --- Activate virtual environment ---
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# --- Install Python requirements ---
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# --- Credentials Instructions (early) ---
echo "=== IMPORTANT: API Keys Required ==="
echo "1. Create an OpenAI API key: https://platform.openai.com/account/api-keys"
echo "2. Enable Gmail API in Google Cloud Console: https://console.cloud.google.com/apis/library/gmail.googleapis.com"
echo "3. Create OAuth2 credentials (Desktop app) to get Client ID and Client Secret."
read -p "Press Enter once you have your keys ready..."

# --- Ask for domain early (needed for .env) ---
read -p "Enter your domain (e.g. tarabot.mydomain.com): " DOMAIN

# --- Create .env file ---
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    read -p "Enter Gmail Client ID: " GMAIL_CLIENT_ID
    read -p "Enter Gmail Client Secret: " GMAIL_CLIENT_SECRET
    read -p "Enter OpenAI API Key: " OPENAI_API_KEY

    cat <<EOF > .env
GMAIL_CLIENT_ID=$GMAIL_CLIENT_ID
GMAIL_CLIENT_SECRET=$GMAIL_CLIENT_SECRET
OPENAI_API_KEY=$OPENAI_API_KEY
# Set to False in prod env
FLASK_DEBUG=False
# Set to production in prod env
FLASK_ENV=production
BASE_URL=https://$DOMAIN
EOF
    echo ".env created successfully!"
else
    echo ".env already exists. Skipping creation."
fi

# --- Verify token.json ---
python - <<'PY'
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import sys

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
try:
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId="me").execute()
    print(f"Token works! Authenticated as: {profile['emailAddress']}")
except Exception as e:
    print(f"token.json exists but could not be validated: {e}")
    sys.exit(1)
PY

echo "token.json validated successfully."

# --- Run manage_users.py to add initial user ---
read -p "Enter admin username: " ADMIN_USERNAME
read -p "Enter admin password: " ADMIN_PASSWORD
python manage_users.py add --username "$ADMIN_USERNAME" --password "$ADMIN_PASSWORD"

# --- Install Caddy if missing ---
if ! command -v caddy >/dev/null 2>&1; then
    echo "Installing Caddy..."
    sudo apt update
    sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | \
        sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | \
        sudo tee /etc/apt/sources.list.d/caddy-stable.list
    sudo apt update
    sudo apt install -y caddy
else
    echo "Caddy already installed."
fi

# --- Check if Caddyfile exists ---
CADDYFILE="/etc/caddy/Caddyfile"
if [ -f "$CADDYFILE" ]; then
    echo "Caddyfile exists at $CADDYFILE."
    read -p "Append TaraBot config to Caddyfile? (y/n): " APPEND
    if [ "$APPEND" = "y" ]; then
        sudo tee -a "$CADDYFILE" > /dev/null <<EOF

$DOMAIN {
    handle /feedback* {
        reverse_proxy localhost:5000
    }
    handle_path /* {
        reverse_proxy localhost:8501
    }
}
EOF
        echo "Appended config to Caddyfile."
    else
        echo "Skipping Caddyfile modification."
    fi
else
    echo "Creating new Caddyfile..."
    sudo tee "$CADDYFILE" > /dev/null <<EOF
$DOMAIN {
    handle /feedback* {
        reverse_proxy localhost:5000
    }
    handle_path /* {
        reverse_proxy localhost:8501
    }
}
EOF
fi

# --- Reload Caddy ---
sudo systemctl reload caddy
echo "Caddy reloaded. Your site should be accessible at https://$DOMAIN"

# --- Final instructions ---
echo "=== Setup Complete ==="
echo "Run apps using nohup:"
echo "  nohup .venv/bin/streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port 8501 &"
echo "  nohup .venv/bin/python feedback/feedback_server.py &"
echo "Visit: https://$DOMAIN"