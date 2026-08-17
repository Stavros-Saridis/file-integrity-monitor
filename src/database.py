import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'fim.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS baseline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT UNIQUE NOT NULL,
            hash TEXT NOT NULL,
            size INTEGER,
            last_modified REAL,
            created_at TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            filepath TEXT NOT NULL,
            old_hash TEXT,
            new_hash TEXT,
            description TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully.")

if __name__ == "__main__":
    init_db()