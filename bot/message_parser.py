# bot/message_parser.py
import base64
import re
from html import unescape
from typing import Tuple, Dict
from email import message_from_bytes, message

def normalize_soft_linebreaks(text: str) -> str:
    """
    Replaces single newlines (soft line breaks) with spaces,
    while preserving double newlines (paragraph breaks).
    """
    return re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

def strip_html(html: str) -> str:
    """
    Remove HTML tags and unescape entities.
    """
    return unescape(re.sub(r'<[^>]+>', '', html)).strip()

def decode_raw_message(raw_message: Dict) -> Tuple[message.Message, Dict]:
    """
    Decode a raw Gmail message payload into a MIME message and metadata.

    :param raw_message: Gmail API message response with 'raw' and metadata
    :return: (MIME message, metadata dict)
    """
    msg_bytes = base64.urlsafe_b64decode(raw_message['raw'].encode('UTF-8'))
    mime_msg = message_from_bytes(msg_bytes)
    return mime_msg, raw_message

def extract_subject(mime_msg: message.Message) -> str:
    """
    Extract Subject header or return an empty string.
    """
    return mime_msg['Subject'] or ''

def extract_body(mime_msg: message.Message) -> str:
    """
    Extract the message body as plain text. If multipart, pick the text/plain part.
    """
    if mime_msg.is_multipart():
        for part in mime_msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain':
                return part.get_payload(decode=True).decode()
    return mime_msg.get_payload(decode=True).decode()
