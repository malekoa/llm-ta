import os
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email import message_from_bytes
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_service():
    creds = Credentials(
        token=None,
        refresh_token=os.getenv("GMAIL_REFRESH_TOKEN"),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=os.getenv("GMAIL_CLIENT_ID"),
        client_secret=os.getenv("GMAIL_CLIENT_SECRET"),
        scopes=SCOPES
    )
    return build('gmail', 'v1', credentials=creds)

def get_unread_messages(service):
    response = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD']).execute()
    messages = response.get('messages', [])
    return messages

def get_message_detail(service, msg_id):
    message = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
    msg_bytes = base64.urlsafe_b64decode(message['raw'].encode('UTF-8'))
    mime_msg = message_from_bytes(msg_bytes)
    return mime_msg, message
