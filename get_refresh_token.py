from google_auth_oauthlib.flow import InstalledAppFlow
import json
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Use your client_id and client_secret from .env or credentials.json
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

creds = flow.run_local_server(port=8080, open_browser=False)

# Save the credentials
with open("token.json", "w") as token:
    token.write(creds.to_json())

print("token.json saved successfully!")
