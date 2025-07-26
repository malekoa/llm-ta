import time
import logging
import markdown2
from email.utils import parseaddr
from email.mime.text import MIMEText
from email_reply_parser import EmailReplyParser

from bot.database import Database
from bot.gmail_client import GmailClient
from bot.responder import Responder
from bot.message_parser import (
    decode_raw_message,
    extract_subject,
    extract_body,
    normalize_soft_linebreaks,
    strip_html
)

MAX_LOG_LENGTH = 300  # truncate large strings for logging

def truncate_for_log(text: str, length: int = MAX_LOG_LENGTH) -> str:
    """Truncate long text for safe logging."""
    return (text[:length] + "...(truncated)") if len(text) > length else text


class MessageHandler:
    """
    Orchestrates reading an unread message, saving it,
    generating a reply (Markdown), converting to HTML, sending, and marking it as read.
    """

    def __init__(self, gmail: GmailClient, db: Database, responder: Responder):
        self.gmail = gmail
        self.db = db
        self.responder = responder

    def handle_single(self, msg_id: str):
        logging.info(f"Handling message {msg_id}")
        raw_msg = self.gmail.get_raw(msg_id)

        # Decode raw Gmail message into MIME
        mime_msg, meta = decode_raw_message(raw_msg)
        timestamp = int(meta.get("internalDate", "0")) // 1000
        thread_id = meta['threadId']
        sender_email = parseaddr(mime_msg['From'])[1]
        sender_id = self.db.hash_email(sender_email)
        subject = extract_subject(mime_msg)

        # Extract and normalize user input
        body_raw = extract_body(mime_msg)
        user_input = EmailReplyParser.parse_reply(body_raw)
        user_input = normalize_soft_linebreaks(user_input)

        logging.info(
            f"Received email from {sender_email} (thread: {thread_id}) "
            f"subject: {subject}, body preview: {truncate_for_log(user_input)}"
        )

        # Save the original user message
        self.db.save_message(
            msg_id, thread_id, sender_email, subject,
            user_input, is_from_bot=0, timestamp=timestamp
        )

        # --- Use old summary for the response ---
        current_summary = self.db.get_sender_summary(sender_id)
        summary_context = [
            (None, f"Sender summary:\n{current_summary}", 0),
            (None, user_input, 0)
        ]
        response_markdown = self.responder.generate(subject, summary_context)

        logging.info(
            f"AI Markdown response generated for {sender_email}: "
            f"{truncate_for_log(response_markdown)}"
        )

        # Convert Markdown → HTML
        response_html = markdown2.markdown(response_markdown)

        # Prepare bot reply (HTML footer + cleaned previous footers)
        bot_msg_id = msg_id + "_bot"
        reply_html = (
            self.responder.HTML_HEADER
            .replace("THREAD_ID_PLACEHOLDER", thread_id)
            .replace("MESSAGE_ID_PLACEHOLDER", bot_msg_id)
            + self.responder.remove_previous_footer(response_html)
        )

        # Save bot message (store Markdown, not HTML)
        self.db.save_message(
            bot_msg_id, thread_id, "me", f"Re: {subject}",
            response_markdown, is_from_bot=1,
            timestamp=int(time.time())
        )

        # Send the reply and mark original as read
        self._send_reply(thread_id, sender_email, reply_html,
                        mime_msg['Message-ID'], subject)
        self.gmail.mark_as_read(msg_id)
        logging.info(f"Reply sent and message {msg_id} marked as read.")

        # --- Update the sender summary after sending ---
        new_summary = self.responder.summarize_sender(current_summary, user_input)
        self.db.update_sender_summary(sender_id, new_summary)



    def _send_reply(self, thread_id, to_email, html_body, original_msg_id, subject):
        if not original_msg_id.startswith('<'):
            original_msg_id = f"<{original_msg_id}>"

        msg = MIMEText(html_body, 'html')
        msg['To'] = to_email
        msg['Subject'] = f"Re: {subject}"
        msg['In-Reply-To'] = original_msg_id
        msg['References'] = original_msg_id

        raw = msg.as_bytes()
        from base64 import urlsafe_b64encode
        encoded = urlsafe_b64encode(raw).decode()
        logging.debug(f"Sending reply to {to_email} (thread {thread_id})")
        self.gmail.send(encoded, thread_id)