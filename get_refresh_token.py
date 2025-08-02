from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
import sys
import json
import socket

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": os.getenv("GMAIL_CLIENT_ID"),
            "client_secret": os.getenv("GMAIL_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    },
    SCOPES
)

# --- Find a free port ---
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(('', 0))
    free_port = s.getsockname()[1]

print(f"Using free port: {free_port}")

# Run the OAuth flow on the free port
creds = flow.run_local_server(port=free_port, open_browser=True)

# Save the credentials
with open("token.json", "w") as token_file:
    token_file.write(creds.to_json())

# Validate token.json
if not os.path.exists("token.json"):
    print("❌ token.json not created.")
    sys.exit(1)

with open("token.json") as token_file:
    data = json.load(token_file)

if not any(k in data for k in ("token", "refresh_token")):
    print("⚠ token.json created but missing expected fields!")
    sys.exit(1)

try:
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId="me").execute()
    print(f"✅ Token works! Authenticated as: {profile['emailAddress']}")
except Exception as e:
    print(f"❌ token.json exists but could not be validated: {e}")
    sys.exit(1)