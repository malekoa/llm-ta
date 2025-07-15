import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "../shared/schema.sql")

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")

# Load schema.sql once
with open(SCHEMA_PATH, "r") as f:
    conn.executescript(f.read())

cursor = conn.cursor()

def hash_email(email):
    return hashlib.sha256(email.encode()).hexdigest()

def save_message(msg_id, thread_id, sender, subject, body, is_from_bot, timestamp):
    sender_hash = hash_email(sender)
    cursor.execute('INSERT OR IGNORE INTO senders (id) VALUES (?)', (sender_hash,))
    cursor.execute('''
        INSERT OR REPLACE INTO messages (id, thread_id, sender_id, subject, body, is_from_bot, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (msg_id, thread_id, sender_hash, subject, body, is_from_bot, timestamp))
    conn.commit()
