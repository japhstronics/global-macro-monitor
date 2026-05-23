"""
visit_tracker.py — Tracks unique visitor IPs using SQLite.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "visits.db")

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            ip          TEXT PRIMARY KEY,
            first_seen  TEXT NOT NULL,
            last_seen   TEXT NOT NULL,
            visit_count INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    return conn

def record_visit(ip: str):
    """Insert new IP or update existing one. Returns (total_unique, is_new)."""
    now = datetime.utcnow().isoformat()
    with _get_conn() as conn:
        existing = conn.execute(
            "SELECT visit_count FROM visits WHERE ip = ?", (ip,)
        ).fetchone()

        if existing:
            conn.execute(
                "UPDATE visits SET last_seen = ?, visit_count = visit_count + 1 WHERE ip = ?",
                (now, ip)
            )
            is_new = False
        else:
            conn.execute(
                "INSERT INTO visits (ip, first_seen, last_seen, visit_count) VALUES (?, ?, ?, 1)",
                (ip, now, now)
            )
            is_new = True

        total = conn.execute("SELECT COUNT(*) FROM visits").fetchone()[0]
    return total, is_new

def get_unique_visit_count() -> int:
    """Returns total number of unique IPs ever seen."""
    with _get_conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM visits").fetchone()[0]