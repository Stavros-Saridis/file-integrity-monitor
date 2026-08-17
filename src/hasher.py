import hashlib
import os

def calculate_hash(filepath):
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except (IOError, PermissionError):
        return None

def scan_directory(directory):
    files = {}
    for root, dirs, filenames in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for filename in filenames:
            if filename.startswith('.'):
                continue
            filepath = os.path.join(root, filename)
            file_hash = calculate_hash(filepath)
            if file_hash:
                stat = os.stat(filepath)
                files[filepath] = {
                    'hash': file_hash,
                    'size': stat.st_size,
                    'last_modified': stat.st_mtime
                }
    return files