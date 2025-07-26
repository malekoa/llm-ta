import sqlite3
import hashlib
from typing import List, Tuple
from bot.config import Config


class Database:
    """
    Provides a wrapper around the SQLite database for storing and
    retrieving email messages and senders.
    """
    def __init__(self):
        # Establish a connection to the SQLite database
        self.conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
        # Ensure foreign key constraints are enforced
        self.conn.execute("PRAGMA foreign_keys = ON;")
        # Load and apply schema definitions
        with open(Config.SCHEMA_PATH, "r") as f:
            self.conn.executescript(f.read())
        # Create a cursor for executing queries
        self.cursor = self.conn.cursor()

    @staticmethod
    def hash_email(email: str) -> str:
        """
        Compute a stable SHA256 hash of the sender's email address.
        This keeps real email addresses out of our database.
        """
        return hashlib.sha256(email.encode("utf-8")).hexdigest()

    def save_message(
        self,
        msg_id: str,
        thread_id: str,
        sender_email: str,
        subject: str,
        body: str,
        is_from_bot: int,
        timestamp: int,
    ) -> None:
        """
        Save a message to the database. If the sender is new,
        insert them into the senders table first.

        :param msg_id: Unique message identifier
        :param thread_id: Thread identifier for grouping messages
        :param sender_email: Raw sender email address
        :param subject: Email subject line
        :param body: Plain-text content of the message
        :param is_from_bot: 1 if sent by our bot, 0 otherwise
        :param timestamp: UNIX timestamp of when the message arrived
        """
        sender_hash = self.hash_email(sender_email)
        # Ensure the sender is present in the senders table
        self.cursor.execute(
            "INSERT OR IGNORE INTO senders (id) VALUES (?)",
            (sender_hash,)
        )
        # Insert or update the message record
        self.cursor.execute(
            """
            INSERT OR REPLACE INTO messages
              (id, thread_id, sender_id, subject, body, is_from_bot, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (msg_id, thread_id, sender_hash, subject, body, is_from_bot, timestamp),
        )
        # Commit changes so they’re saved to disk
        self.conn.commit()

    def get_thread_messages(self, thread_id: str) -> List[Tuple[str, str, int]]:
        """
        Retrieve all messages in a thread, ordered by timestamp ascending.

        :param thread_id: The thread identifier
        :return: List of tuples (sender_id, body, is_from_bot)
        """
        self.cursor.execute(
            """
            SELECT sender_id, body, is_from_bot
            FROM messages
            WHERE thread_id = ?
            ORDER BY timestamp ASC
            """,
            (thread_id,),
        )
        return self.cursor.fetchall()

    def get_sender_summary(self, sender_id: str) -> str:
        self.cursor.execute(
            "SELECT summary FROM senders WHERE id = ?", (sender_id,)
        )
        row = self.cursor.fetchone()
        return row[0] if row else ""

    def update_sender_summary(self, sender_id: str, new_summary: str) -> None:
        self.cursor.execute(
            """
            INSERT INTO senders (id, summary)
            VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET summary = excluded.summary
            """,
            (sender_id, new_summary),
        )
        self.conn.commit()


    def close(self) -> None:
        """
        Close the database connection when done to free resources.
        """
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.conn.close()
