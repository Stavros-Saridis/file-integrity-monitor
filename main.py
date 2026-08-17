import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.database import init_db, get_connection
from src.hasher import scan_directory, calculate_hash
from src.alerter import save_event
from src.watcher import start_watching

WATCHED_DIR = os.path.join(os.path.dirname(__file__), 'watched_folder')

def build_baseline():
    print(f"[*] Scanning directory: {WATCHED_DIR}")
    files = scan_directory(WATCHED_DIR)

    if not files:
        print("[!] No files found — add some files to watched_folder first")
        return False

    conn = get_connection()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for filepath, info in files.items():
        conn.execute('''
            INSERT OR REPLACE INTO baseline (filepath, hash, size, last_modified, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (filepath, info['hash'], info['size'], info['last_modified'], timestamp))

    conn.commit()
    conn.close()
    print(f"[DB] Baseline saved — {len(files)} files indexed.")
    return True

if __name__ == "__main__":
    print("[*] Initializing database...")
    init_db()

    print("[*] Building baseline...")
    if not build_baseline():
        print("[!] Add files to watched_folder and restart.")
        sys.exit(1)

    print("[*] Starting file integrity monitor — press Ctrl+C to stop")
    start_watching(WATCHED_DIR)