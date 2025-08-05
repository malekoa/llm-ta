import time
import json
import sqlite3
import hashlib
from datetime import datetime
from typing import List, Tuple
from bot.config import Config
from werkzeug.security import generate_password_hash, check_password_hash


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

    def add_document(self, filename: str, content: str):
        self.cursor.execute(
            "INSERT INTO documents (filename, content) VALUES (?, ?)",
            (filename, content),
        )
        self.conn.commit()

    def update_document_name(self, doc_id: int, new_filename: str):
        self.cursor.execute(
            "UPDATE documents SET filename = ? WHERE id = ?",
            (new_filename, doc_id),
        )
        self.conn.commit()

    def delete_document(self, doc_id: int):
        self.cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        self.conn.commit()

    def list_documents(self):
        self.cursor.execute(
            "SELECT id, filename, length(content) as size, created_at FROM documents"
        )
        return self.cursor.fetchall()

    def get_document_content(self, doc_id: int):
        self.cursor.execute("SELECT content FROM documents WHERE id = ?", (doc_id,))
        row = self.cursor.fetchone()
        return row[0] if row else ""
    
    def add_chunk(self, document_id: int, chunk_index: int, content: str):
        self.cursor.execute(
            "INSERT INTO document_chunks (document_id, chunk_index, content) VALUES (?, ?, ?)",
            (document_id, chunk_index, content)
        )
        self.conn.commit()

    def get_chunks_for_document(self, document_id: int):
        self.cursor.execute(
            "SELECT chunk_index, content FROM document_chunks WHERE document_id = ? ORDER BY chunk_index",
            (document_id,)
        )
        return self.cursor.fetchall()
    
    def list_document_chunks(self, document_id: int):
        """
        Return all chunks for a given document, ordered by index.
        """
        self.cursor.execute(
            """
            SELECT id, chunk_index, length(content) as size, content
            FROM document_chunks
            WHERE document_id = ?
            ORDER BY chunk_index
            """,
            (document_id,)
        )
        return self.cursor.fetchall()
    
    def update_chunk_embedding(self, chunk_id: int, embedding: list[float]):
        if embedding is None:
            embedding_json = None
        else:
            embedding_json = json.dumps(embedding)
        self.cursor.execute(
            "UPDATE document_chunks SET embedding = ? WHERE id = ?",
            (embedding_json, chunk_id)
        )
        self.conn.commit()

    def document_has_embeddings(self, document_id: int) -> bool:
        self.cursor.execute(
            """
            SELECT COUNT(*) 
            FROM document_chunks 
            WHERE document_id = ? 
            AND (embedding IS NULL OR embedding = '')
            """,
            (document_id,)
        )
        missing_count = self.cursor.fetchone()[0]
        return missing_count == 0

    def close(self) -> None:
        """
        Close the database connection when done to free resources.
        Ensures WAL is checkpointed so no -wal/-shm files remain.
        """
        try:
            self.conn.execute("PRAGMA wal_checkpoint(FULL);")
        except Exception as e:
            print(f"Error checkpointing WAL: {e}")
        self.conn.close()

    def ensure_user_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()


    def add_user(self, username: str, password: str):
        try:
            password_hash = generate_password_hash(password)
            self.cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def list_users(self):
        self.cursor.execute("SELECT id, username, created_at FROM users ORDER BY id")
        return self.cursor.fetchall()

    def update_password(self, username: str, new_password: str):
        password_hash = generate_password_hash(new_password)
        self.cursor.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (password_hash, username)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_user(self, username: str):
        self.cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def verify_user(self, username: str, password: str) -> bool:
        self.cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        row = self.cursor.fetchone()
        return row and check_password_hash(row[0], password)
    
    def add_vote(self, message_id: str, vote: str):
        """
        Insert or update a vote for a given message_id.
        """
        self.cursor.execute("""
            INSERT INTO votes (message_id, vote)
            VALUES (?, ?)
            ON CONFLICT(message_id) DO UPDATE SET vote = excluded.vote
        """, (message_id, vote))
        self.conn.commit()

    def ensure_settings_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        self.conn.commit()
        # Default sender limit if not set
        self.cursor.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            ("daily_sender_limit", "10")
        )
        self.conn.commit()

    def get_setting(self, key: str, default=None):
        self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = self.cursor.fetchone()
        return row[0] if row else default

    def set_setting(self, key: str, value: str):
        self.cursor.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?)"
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value)
        )
        self.conn.commit()

    def count_received_today(self, sender_id: str) -> int:
        """
        Count how many incoming (non-bot) messages from this sender
        have been received today.
        """
        start_of_day = int(time.time() // 86400 * 86400)
        self.cursor.execute("""
            SELECT COUNT(*) FROM messages
            WHERE sender_id = ? AND is_from_bot = 0
            AND timestamp >= ?
        """, (sender_id, start_of_day))
        return self.cursor.fetchone()[0]
    
    def has_sent_limit_warning(self, sender_id: str) -> bool:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        self.cursor.execute(
            "SELECT 1 FROM limit_warnings WHERE sender_id = ? AND date = ?",
            (sender_id, today),
        )
        return self.cursor.fetchone() is not None

    def mark_limit_warning_sent(self, sender_id: str):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        self.cursor.execute(
            "INSERT OR IGNORE INTO limit_warnings (sender_id, date) VALUES (?, ?)",
            (sender_id, today),
        )
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.conn.close()
