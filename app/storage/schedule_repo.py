import sqlite3

class ScheduleRepo:
    def __init__(self, db):
        self.db = db

    def add(self, user_id, title, desc, date, time):
        with sqlite3.connect(self.db.path) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO schedules(user_id,title,description,date,time) VALUES(?,?,?,?,?)",
                (user_id, title, desc, date, time),
            )
            conn.commit()
            return cur.lastrowid

    def get(self, user_id, sid):
        with sqlite3.connect(self.db.path) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id,title,description,date,time FROM schedules WHERE user_id=? AND id=?",
                (user_id, sid),
            )
            return cur.fetchone()

    def list_all(self, user_id):
        with sqlite3.connect(self.db.path) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id,title,description,date,time FROM schedules WHERE user_id=? ORDER BY date,time",
                (user_id,),
            )
            return cur.fetchall()

    def today(self, user_id, today_str):
        with sqlite3.connect(self.db.path) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id,title,description,date,time FROM schedules WHERE user_id=? AND date=? ORDER BY time",
                (user_id, today_str),
            )
            return cur.fetchall()

    def delete(self, user_id, sid):
        with sqlite3.connect(self.db.path) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM schedules WHERE id=? AND user_id=?", (sid, user_id))
            conn.commit()
            return cur.rowcount > 0

    def delete_all(self, user_id):
        with sqlite3.connect(self.db.path) as conn:
            cur = conn.cursor()
            # 리마인더 먼저 지우기
            cur.execute("DELETE FROM reminders WHERE user_id=?", (user_id,))
            cur.execute("DELETE FROM schedules WHERE user_id=?", (user_id,))
            cnt = cur.rowcount
            conn.commit()
            return cnt

    # ---- reminders ----
    def add_reminder(self, user_id, schedule_id, offset_minutes: int):
        with sqlite3.connect(self.db.path) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO reminders(user_id, schedule_id, offset_minutes) VALUES(?,?,?)",
                (user_id, schedule_id, offset_minutes),
            )
            conn.commit()
            return cur.lastrowid

    def list_reminders_for_user(self, user_id):
        with sqlite3.connect(self.db.path) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, schedule_id, offset_minutes FROM reminders WHERE user_id=?",
                (user_id,),
            )
            return cur.fetchall()


    # 알림 단건 삭제
    def delete_reminder(self, user_id: int, reminder_id: int) -> bool:
        with sqlite3.connect(self.db.path) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM reminders WHERE id=? AND user_id=?", (reminder_id, user_id))
            conn.commit()
            return cur.rowcount > 0

    # 특정 일정의 모든 알림 삭제
    def delete_reminders_for_schedule(self, user_id: int, schedule_id: int):
        with sqlite3.connect(self.db.path) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM reminders WHERE user_id=? AND schedule_id=?", (user_id, schedule_id))
            conn.commit()

    # 사용자 전체 알림 목록 (+ 일정 정보 조인)
    # 반환: [(reminder_id, schedule_id, offset_minutes, title, desc, date, time)]
    def list_reminders_detailed(self, user_id: int):
        with sqlite3.connect(self.db.path) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.id, r.schedule_id, r.offset_minutes,
                       s.title, s.description, s.date, s.time
                  FROM reminders r
                  JOIN schedules s ON s.id = r.schedule_id
                 WHERE r.user_id=?
                 ORDER BY s.date ASC, s.time ASC, r.offset_minutes ASC
            """, (user_id,))
            return cur.fetchall()
