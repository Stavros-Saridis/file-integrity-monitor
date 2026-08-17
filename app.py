from flask import Flask, render_template, jsonify
from src.database import init_db, get_connection
from src.alerter import get_recent_events, get_event_stats

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events')
def api_events():
    events = get_recent_events(50)
    return jsonify([dict(e) for e in events])

@app.route('/api/stats')
def api_stats():
    return jsonify(get_event_stats())

@app.route('/api/baseline')
def api_baseline():
    conn = get_connection()
    files = conn.execute('''
        SELECT filepath, hash, size, created_at
        FROM baseline
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(f) for f in files])

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)