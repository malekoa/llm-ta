import base64
from email.utils import parseaddr
from html import unescape
from email_reply_parser import EmailReplyParser
from gmail_client import get_service, get_unread_messages, get_message_detail
from responder import generate_response, HTML_HEADER, remove_previous_footer
from database import save_message
import re
import time

def extract_body(mime_msg):
    if mime_msg.is_multipart():
        for part in mime_msg.walk():
            if part.get_content_type() == 'text/plain':
                return part.get_payload(decode=True).decode()
    return mime_msg.get_payload(decode=True).decode()

def extract_subject(mime_msg):
    return mime_msg['Subject'] or ''

def strip_html(html):
    text = re.sub(r'<[^>]+>', '', html)
    return unescape(text).strip()

def format_reply_html(reply_text, thread_id, bot_message_id):
    """Prepends the disclaimer/footer to the cleaned response."""
    footer = HTML_HEADER \
        .replace("THREAD_ID_PLACEHOLDER", thread_id) \
        .replace("MESSAGE_ID_PLACEHOLDER", bot_message_id)
    return footer + remove_previous_footer(reply_text).strip()

def send_reply(service, thread_id, to_email, html_body, original_msg_id, subject):
    from email.mime.text import MIMEText
    if not original_msg_id.startswith('<'):
        original_msg_id = f"<{original_msg_id}>"

    msg = MIMEText(html_body, 'html')
    msg['To'] = to_email
    msg['Subject'] = f"Re: {subject}"
    msg['In-Reply-To'] = original_msg_id
    msg['References'] = original_msg_id

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(
        userId="me",
        body={'raw': raw, 'threadId': thread_id}
    ).execute()

def handle_message(service, msg_meta):
    mime_msg, full_msg = get_message_detail(service, msg_meta['id'])
    timestamp_ms = int(full_msg.get("internalDate", "0"))  # in milliseconds
    timestamp = timestamp_ms // 1000  # convert to seconds
    sender_email = parseaddr(mime_msg['From'])[1]
    subject = extract_subject(mime_msg)
    body_raw = extract_body(mime_msg)
    thread_id = full_msg['threadId']
    original_msg_id = mime_msg['Message-ID']

    print(f"Responding to: {sender_email}")

    user_input = EmailReplyParser.parse_reply(body_raw)
    response_html = generate_response(subject, user_input)

    # Save original user message
    save_message(msg_meta['id'], thread_id, sender_email, subject, user_input, is_from_bot=0, timestamp=timestamp)

    # Prepare bot reply
    bot_msg_id = msg_meta['id'] + "_bot"
    reply_html = format_reply_html(response_html, thread_id, bot_msg_id)
    # # Save bot message without HTML
    save_message(bot_msg_id, thread_id, 'me', f"Re: {subject}", strip_html(response_html), is_from_bot=1, timestamp=int(time.time()))

    # Send response
    send_reply(service, thread_id, sender_email, reply_html, original_msg_id, subject)

    # Mark original message as read
    service.users().messages().modify(userId='me', id=msg_meta['id'], body={'removeLabelIds': ['UNREAD']}).execute()

def main():
    service = get_service()
    for msg in get_unread_messages(service):
        handle_message(service, msg)

if __name__ == '__main__':
    main()
