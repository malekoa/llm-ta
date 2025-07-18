PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS senders (
    id TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    thread_id TEXT,
    sender_id TEXT,
    subject TEXT,
    body TEXT,
    is_from_bot INTEGER,
    timestamp INTEGER,
    FOREIGN KEY (sender_id) REFERENCES senders(id)
);

CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL UNIQUE,
    vote TEXT CHECK(vote IN ('up', 'down')),
    FOREIGN KEY (message_id) REFERENCES messages(id)
);
