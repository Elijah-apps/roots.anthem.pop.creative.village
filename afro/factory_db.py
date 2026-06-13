import sqlite3
import json
from datetime import datetime

DB_NAME = "beat_factory.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Table for Becomes/Genomes
    c.execute('''CREATE TABLE IF NOT EXISTS beats (
        hex_id TEXT PRIMARY KEY,
        title TEXT,
        bpm REAL,
        swing REAL,
        genome_json TEXT,
        composite_score REAL,
        user_preference INTEGER DEFAULT 0,
        kg_state_json TEXT,
        timestamp DATETIME
    )''')
    # Table for Trial History
    c.execute('''CREATE TABLE IF NOT EXISTS trials (
        trial_id INTEGER PRIMARY KEY AUTOINCREMENT,
        hex_id TEXT,
        score REAL,
        params_json TEXT
    )''')
    conn.commit()
    conn.close()

def save_beat(hex_id, title, bpm, swing, genome, score, kg_state=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO beats
                 (hex_id, title, bpm, swing, genome_json, composite_score, kg_state_json, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (hex_id, title, bpm, swing, json.dumps(genome), score, json.dumps(kg_state) if kg_state else None, datetime.now()))
    conn.commit()
    conn.close()

def update_preference(hex_id, preference):
    """preference: 1 for like, -1 for dislike"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE beats SET user_preference = ? WHERE hex_id = ?', (preference, hex_id))
    conn.commit()
    conn.close()

def get_top_genomes(limit=10):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM beats ORDER BY composite_score DESC LIMIT ?', (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
