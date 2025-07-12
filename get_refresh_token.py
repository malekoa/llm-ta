from google_auth_oauthlib.flow import InstalledAppFlow
import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

client_id = os.getenv("GMAIL_CLIENT_ID")
client_secret = os.getenv("GMAIL_CLIENT_SECRET")

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    },
    SCOPES
)

creds = flow.run_local_server(port=8080, open_browser=False)
print("ACCESS TOKEN:", creds.token)
print("REFRESH TOKEN:", creds.refresh_token)
