import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from bot.config import Config

# Path to OAuth token file (contains access + refresh tokens)
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "token.json")

class GmailClient:
    """
    Gmail API client wrapper.
    Provides helper methods for reading unread emails,
    fetching raw messages, sending replies, and marking messages as read.
    """

    def __init__(self):
        """
        Initialize the Gmail API client.

        Loads credentials from token.json (generated via OAuth flow),
        refreshes the access token if expired, and builds the Gmail service.
        """
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, Config.GMAIL_SCOPES)
        else:
            raise RuntimeError(
                "token.json not found. Run the token generation script first "
                "to authenticate and store credentials."
            )

        # Build the Gmail API service using authorized credentials
        self.service = build("gmail", "v1", credentials=creds)

    def list_unread(self):
        """
        Retrieve metadata for all unread messages in the user's inbox.
        
        Returns:
            List of message metadata dictionaries (id, threadId, etc.)
        """
        resp = self.service.users().messages().list(
            userId="me", labelIds=["INBOX", "UNREAD"]
        ).execute()
        return resp.get("messages", [])

    def get_raw(self, msg_id: str):
        """
        Fetch the full raw RFC822 message payload for a given message ID.
        
        Args:
            msg_id: The Gmail message ID.
        
        Returns:
            Gmail API response containing base64-encoded raw message data.
        """
        return self.service.users().messages().get(
            userId="me", id=msg_id, format="raw"
        ).execute()

    def send(self, raw_message: str, thread_id: str):
        """
        Send an email reply within an existing thread.
        
        Args:
            raw_message: Base64-encoded RFC822 message.
            thread_id: Gmail thread ID to append the reply to.
        """
        self.service.users().messages().send(
            userId="me", body={"raw": raw_message, "threadId": thread_id}
        ).execute()

    def mark_as_read(self, msg_id: str):
        """
        Remove the 'UNREAD' label from a message, marking it as read.
        
        Args:
            msg_id: The Gmail message ID to mark as read.
        """
        self.service.users().messages().modify(
            userId="me", id=msg_id, body={"removeLabelIds": ["UNREAD"]}
        ).execute()