import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
from src.hasher import calculate_hash
from src.database import get_connection
from src.alerter import save_event

class FIMEventHandler(FileSystemEventHandler):

    def on_modified(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        new_hash = calculate_hash(filepath)
        if not new_hash:
            return

        conn = get_connection()
        row = conn.execute(
            'SELECT hash FROM baseline WHERE filepath = ?', (filepath,)
        ).fetchone()
        conn.close()

        if row:
            old_hash = row['hash']
            if new_hash != old_hash:
                save_event(
                    event_type="FILE_MODIFIED",
                    severity="CRITICAL",
                    filepath=filepath,
                    description=f"Hash changed — file may have been tampered with",
                    old_hash=old_hash,
                    new_hash=new_hash
                )
                conn = get_connection()
                conn.execute(
                    'UPDATE baseline SET hash = ? WHERE filepath = ?',
                    (new_hash, filepath)
                )
                conn.commit()
                conn.close()

    def on_created(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        new_hash = calculate_hash(filepath)
        if not new_hash:
            return

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        import os
        stat = os.stat(filepath)
        conn = get_connection()
        conn.execute('''
            INSERT OR REPLACE INTO baseline (filepath, hash, size, last_modified, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (filepath, new_hash, stat.st_size, stat.st_mtime, timestamp))
        conn.commit()
        conn.close()

        save_event(
            event_type="FILE_CREATED",
            severity="HIGH",
            filepath=filepath,
            description=f"New file detected in monitored directory",
            new_hash=new_hash
        )

    def on_deleted(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        save_event(
            event_type="FILE_DELETED",
            severity="CRITICAL",
            filepath=filepath,
            description=f"File was deleted from monitored directory"
        )
        conn = get_connection()
        conn.execute('DELETE FROM baseline WHERE filepath = ?', (filepath,))
        conn.commit()
        conn.close()

def start_watching(directory):
    event_handler = FIMEventHandler()
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()
    print(f"[*] Watching directory: {directory}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()