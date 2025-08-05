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
        # Fetch raw message
        raw_msg = self.gmail.get_raw(msg_id)

        # Decode and parse
        mime_msg, meta = decode_raw_message(raw_msg)
        timestamp = int(meta.get("internalDate", "0")) // 1000
        thread_id = meta['threadId']
        sender_email = parseaddr(mime_msg['From'])[1]
        sender_id = self.db.hash_email(sender_email)
        subject = extract_subject(mime_msg)

        # Exit early if wrong plus address
        plus_filter = self.db.get_setting("plus_address", "")
        if plus_filter:
            to_email = parseaddr(mime_msg.get('To', ''))[1].lower()
            if f"+{plus_filter.lower()}@" not in to_email:
                logging.info(f"Skipping message {msg_id}: does not match plus address filter ({plus_filter})")
                self.gmail.mark_as_read(msg_id)  # optional: mark as read to avoid repeated checks
                return


        # Exit early if past sender limit
        sender_limit_enabled = self.db.get_setting("sender_limit_enabled", "1") == "1"
        if sender_limit_enabled:
            daily_limit = int(self.db.get_setting("daily_sender_limit", "10"))
            received_today = self.db.count_received_today(sender_id)
            logging.info(f"Sender {sender_email} has sent {received_today} messages today.")
            if received_today > daily_limit:
                logging.info(f"Sender {sender_email} exceeded daily message limit ({daily_limit}).")

                # Send warning only once per day
                if not self.db.has_sent_limit_warning(sender_id):
                    warning_html = """
                    <p>Hello,</p>
                    <p>You have exceeded the allowed number of emails for today. 
                    Please wait until tomorrow to send more messages.</p>
                    <p>Thank you,</p>
                    <p>Tara</p>
                    """
                    self._send_reply(thread_id, sender_email, warning_html, mime_msg['Message-ID'], subject)
                    self.db.mark_limit_warning_sent(sender_id)
                    logging.info(f"Sent daily limit warning to {sender_email}")
                else:
                    logging.info(f"Daily limit warning already sent to {sender_email}")

                self.gmail.mark_as_read(msg_id)
                return

        # Extract user input
        body_raw = extract_body(mime_msg)
        user_input = EmailReplyParser.parse_reply(body_raw)
        user_input = normalize_soft_linebreaks(user_input)

        # Log only sender + thread info
        logging.info(f"New email received from {sender_email} (thread {thread_id})")

        # Save message
        self.db.save_message(
            msg_id, thread_id, sender_email, subject,
            user_input, is_from_bot=0, timestamp=timestamp
        )

        # Generate AI response
        current_summary = self.db.get_sender_summary(sender_id)
        response_markdown = self.responder.generate(
            subject=subject,
            sender_summary=current_summary,
            latest_message=user_input
        )

        # Convert Markdown → HTML
        response_html = markdown2.markdown(response_markdown)

        # Prepare bot reply
        bot_msg_id = msg_id + "_bot"
        reply_html = (
            self.responder.HTML_HEADER
            .replace("THREAD_ID_PLACEHOLDER", thread_id)
            .replace("MESSAGE_ID_PLACEHOLDER", bot_msg_id)
            + self.responder.remove_previous_footer(response_html)
        )

        # Save bot message
        self.db.save_message(
            bot_msg_id, thread_id, "me", f"Re: {subject}",
            response_markdown, is_from_bot=1,
            timestamp=int(time.time())
        )

        # Determine which of our addresses was used (includes plus if present)
        original_to = parseaddr(mime_msg.get('Delivered-To', mime_msg.get('To', '')))[1]

        # Send and mark as read, passing original_to so thread continuity is preserved
        self._send_reply(thread_id, sender_email, reply_html, mime_msg['Message-ID'], subject, original_to)
        self.gmail.mark_as_read(msg_id)

        # Log only summary action
        logging.info(f"Response sent to {sender_email}")

        # Update sender summary
        new_summary = self.responder.summarize_sender(current_summary, user_input)
        logging.info(f"Updated summary for {sender_email}")
        self.db.update_sender_summary(sender_id, new_summary)

    def _send_reply(self, thread_id, to_email, html_body, original_msg_id, subject, original_to=None):
        if not original_msg_id.startswith('<'):
            original_msg_id = f"<{original_msg_id}>"

        msg = MIMEText(html_body, 'html')
        msg['To'] = to_email  # always reply to the sender
        if original_to:
            msg['From'] = original_to  # use your +password variant for threading
        else:
            msg['From'] = "me"
        msg['Subject'] = f"Re: {subject}"
        msg['In-Reply-To'] = original_msg_id
        msg['References'] = original_msg_id

        raw = msg.as_bytes()
        from base64 import urlsafe_b64encode
        encoded = urlsafe_b64encode(raw).decode()
        self.gmail.send(encoded, thread_id)