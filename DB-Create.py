import sqlite3

conn = sqlite3.connect("agent.db", check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id TEXT PRIMARY KEY,
    thread_id TEXT,
    role TEXT,
    content TEXT,
    created_at TEXT
)
""")

conn.commit()