import sqlite3
from pathlib import Path

class DB:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _init(self):
        with sqlite3.connect(self.path) as conn:
            c = conn.cursor()
            c.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                schedule_date TEXT NOT NULL,
                schedule_time TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """)
            c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY
            )
            """)
            conn.commit()

    def conn(self):
        return sqlite3.connect(self.path)
