from typing import List, Tuple, Optional
from app.storage.db import DB

class ScheduleRepo:
    def __init__(self, db: DB):
        self.db = db

    def add(self, user_id:int, title:str, description:str, date:str, time:Optional[str]):
        with self.db.conn() as conn:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (user_id,))
            c.execute(
                "INSERT INTO schedules(user_id,title,description,schedule_date,schedule_time) VALUES(?,?,?,?,?)",
                (user_id, title, description, date, time)
            )
            conn.commit()
            return c.lastrowid

    def list_user_ids(self)->List[int]:
        with self.db.conn() as conn:
            c = conn.cursor()
            c.execute("SELECT user_id FROM users")
            return [r[0] for r in c.fetchall()]

    def get_all(self, user_id:int)->List[Tuple]:
        with self.db.conn() as conn:
            c = conn.cursor()
            c.execute(
                "SELECT id,title,description,schedule_date,schedule_time,created_at FROM schedules WHERE user_id=? ORDER BY schedule_date, schedule_time",
                (user_id,)
            )
            return c.fetchall()

    def get_by_date(self, user_id:int, date:str)->List[Tuple]:
        with self.db.conn() as conn:
            c = conn.cursor()
            c.execute(
                "SELECT id,title,description,schedule_date,schedule_time FROM schedules WHERE user_id=? AND schedule_date=? ORDER BY schedule_time",
                (user_id, date)
            )
            return c.fetchall()

    def delete(self, user_id:int, sched_id:int)->bool:
        with self.db.conn() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM schedules WHERE id=? AND user_id=?", (sched_id, user_id))
            conn.commit()
            return c.rowcount > 0
