import sqlite3
import hashlib
import time

conn = sqlite3.connect('bot/data.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    thread_id TEXT,
    sender_hash TEXT,
    subject TEXT,
    body TEXT,
    is_from_bot INTEGER,
    timestamp INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL,
    vote TEXT CHECK(vote IN ('up', 'down')),
    comment TEXT,
    submitted_at INTEGER,
    FOREIGN KEY (message_id) REFERENCES messages(id)
)
''')
conn.commit()

def hash_email(email):
    return hashlib.sha256(email.encode()).hexdigest()

def save_message(msg_id, thread_id, sender, subject, body, is_from_bot, timestamp):
    cursor.execute('''
        INSERT OR REPLACE INTO messages (id, thread_id, sender_hash, subject, body, is_from_bot, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (msg_id, thread_id, hash_email(sender), subject, body, is_from_bot, timestamp))
    conn.commit()