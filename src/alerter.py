from datetime import datetime
from src.database import get_connection

def save_event(event_type, severity, filepath, description, old_hash=None, new_hash=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_connection()
    conn.execute('''
        INSERT INTO events (timestamp, event_type, severity, filepath, old_hash, new_hash, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, event_type, severity, filepath, old_hash, new_hash, description))
    conn.commit()
    conn.close()

    print(f"[{timestamp}] [{severity}] {event_type} — {filepath}")
    print(f"    {description}")

    with open("logs/events.log", "a") as f:
        f.write(f"[{timestamp}] [{severity}] {event_type} | {filepath} | {description}\n")

def get_recent_events(limit=50):
    conn = get_connection()
    events = conn.execute('''
        SELECT * FROM events
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return events

def get_event_stats():
    conn = get_connection()
    total = conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]
    critical = conn.execute('SELECT COUNT(*) FROM events WHERE severity = "CRITICAL"').fetchone()[0]
    high = conn.execute('SELECT COUNT(*) FROM events WHERE severity = "HIGH"').fetchone()[0]
    conn.close()
    return {"total": total, "critical": critical, "high": high}