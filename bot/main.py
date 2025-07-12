from gmail_client import get_service, get_unread_messages, get_message_detail
from responder import generate_response
from database import save_message
from email.utils import parseaddr
import base64

def extract_body(mime_msg):
    if mime_msg.is_multipart():
        for part in mime_msg.walk():
            if part.get_content_type() == 'text/plain':
                return part.get_payload(decode=True).decode()
    else:
        return mime_msg.get_payload(decode=True).decode()

def extract_subject(mime_msg):
    return mime_msg['Subject'] or ''

def send_reply(service, thread_id, to_email, body):
    from email.mime.text import MIMEText
    message = MIMEText(body)
    message['to'] = to_email
    message['subject'] = "Re: your message"
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={'raw': raw, 'threadId': thread_id}).execute()

def main():
    service = get_service()
    messages = get_unread_messages(service)
    for m in messages:
        mime_msg, full_msg = get_message_detail(service, m['id'])
        sender = parseaddr(mime_msg['From'])[1]
        subject = extract_subject(mime_msg)
        body = extract_body(mime_msg)
        thread_id = full_msg['threadId']

        print(f"Responding to: {sender}")
        reply = generate_response(body)

        # Save incoming message in DB
        save_message(m['id'], thread_id, sender, subject, body, is_from_bot=0)

        # Send response and save response to DB
        send_reply(service, thread_id, sender, reply)
        save_message(m['id'] + '_bot', thread_id, 'me', 'Re: ' + subject, reply, is_from_bot=1)

        # Mark as read
        service.users().messages().modify(userId='me', id=m['id'], body={'removeLabelIds': ['UNREAD']}).execute()

if __name__ == '__main__':
    main()
