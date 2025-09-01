# app/storage/db.py
import sqlite3
from pathlib import Path

class DB:
    def __init__(self, path: str):
        self.path = str(Path(path))
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _init(self):
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS schedules(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                description TEXT,
                date TEXT,   -- YYYY-MM-DD
                time TEXT    -- HH:MM or NULL
            )
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS reminders(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                schedule_id INTEGER NOT NULL,
                offset_minutes INTEGER NOT NULL,  -- 0=정각, 30=30분 전, 60, 1440(하루 전) 등
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()
