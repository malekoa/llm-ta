# bot/main.py
import logging

from bot.gmail_client import GmailClient
from bot.database import Database
from bot.responder import Responder
from bot.handler import MessageHandler

logging.basicConfig(
    filename='bot.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    # Initialize components
    gmail = GmailClient()
    db = Database()
    responder = Responder()
    handler = MessageHandler(gmail, db, responder)

    # Process all unread messages
    for msg in gmail.list_unread():
        try:
            handler.handle_single(msg['id'])
        except Exception:
            logging.exception(f"Failed to process message {msg.get('id')}")

if __name__ == '__main__':
    main()
