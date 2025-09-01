# app/services/reminder.py
import datetime
import re
from typing import Optional, Tuple

from telegram.ext import Application, CallbackContext

KST = datetime.timezone(datetime.timedelta(hours=9))

# 0=월, 6=일
_KOR_WEEKDAY = {
    "월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6,
    "월요일": 0, "화요일": 1, "수요일": 2, "목요일": 3, "금요일": 4, "토요일": 5, "일요일": 6,
}


def _next_weekday_date(from_date: datetime.date, weekday: int) -> datetime.date:
    """다음 해당 요일 날짜 반환 (0=월 ... 6=일)"""
    delta = (weekday - from_date.weekday()) % 7
    delta = 7 if delta == 0 else delta
    return from_date + datetime.timedelta(days=delta)


def dday_text(date_str: str, tz: datetime.tzinfo = KST) -> str:
    """YYYY-MM-DD → (D-N / D-DAY / D+N)"""
    today = datetime.datetime.now(tz=tz).date()
    target = datetime.date.fromisoformat(date_str)
    delta = (target - today).days
    if delta == 0:
        return "(D-DAY)"
    elif delta > 0:
        return f"(D-{delta})"
    else:
        return f"(D+{abs(delta)})"


class ReminderService:
    """
    기능
    ----
    1) 자연어 반복 알림 (/remind)
       - '매일 HH:MM 메세지'
       - '매주 요일 HH:MM 메세지'
       - '매주 요일 메세지' (시간 생략 시 09:00)

    2) 일정별 알림 예약 (버튼 rset:<sid>:<offset>)
       - offset_minutes: 0(정각), 30, 60, 1440(하루 전) 등

    3) 복구
       - 앱 시작 후 DB에 저장된 reminders를 읽어 다시 스케줄

    주의
    ----
    - sender.app.bot.send_message 사용 (sender는 PTBSender처럼 app 보유)
    - repo는 ScheduleRepo 구현체여야 함
    """

    def __init__(self, repo, sender):
        self.repo = repo
        self.sender = sender
        self.app: Optional[Application] = None

    # ------------------------------ 초기화/복구 ------------------------------

    def setup(self, app: Application):
        """애플리케이션 연결 및 부팅 복구 예약"""
        self.app = app
        # 부팅 직후 DB에 저장된 reminders 복구
        app.job_queue.run_once(self._restore_all, when=1.0)

    async def _restore_all(self, context: CallbackContext):
        """
        모든 사용자에 대해 reminders 복구.
        간단 구현: schedules에서 DISTINCT user_id를 추출 후 각 사용자의 reminders를 복구.
        """
        import sqlite3

        with sqlite3.connect(self.repo.db.path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT user_id FROM schedules")
            users = [row[0] for row in cur.fetchall()]

        for uid in users:
            try:
                reminders = self.repo.list_reminders_for_user(uid)  # [(id, schedule_id, offset_minutes), ...]
            except Exception:
                continue

            for rid, sid, offset in reminders:
                row = self.repo.get(uid, sid)  # (id,title,desc,date,time) or None
                if row:
                    await self._schedule_one(uid, row, offset, rid)

    # ------------------------------ 자연어 알림 (/remind) ------------------------------

    def _parse_remind_text(self, text: str) -> Tuple[str, Optional[int], Optional[datetime.time], str]:
        """
        Returns: ("daily"|"weekly", weekday_or_None, time_or_None, message)

        지원 패턴:
          - 매일 HH:MM [메시지]
          - 매주 (요일) HH:MM [메시지]
          - 매주 (요일) [메시지]   # HH:MM 생략 → 기본 09:00
        """
        s = re.sub(r"\s+", " ", text).strip()

        # 매일 HH:MM ...
        m = re.match(r"^매일\s+(\d{1,2}):(\d{2})\s+(.*)$", s)
        if m:
            hh, mm = int(m.group(1)), int(m.group(2))
            if not (0 <= hh <= 23 and 0 <= mm <= 59):
                raise ValueError("시간 형식이 올바르지 않습니다.")
            msg = m.group(3).strip()
            return ("daily", None, datetime.time(hh, mm, tzinfo=KST), msg)

        # 매주 요일 HH:MM ...
        m = re.match(r"^매주\s+([월화수목금토일](?:요일)?)\s+(\d{1,2}):(\d{2})\s+(.*)$", s)
        if m:
            wd = _KOR_WEEKDAY.get(m.group(1))
            hh, mm = int(m.group(2)), int(m.group(3))
            if wd is None:
                raise ValueError("요일을 인식하지 못했습니다.")
            if not (0 <= hh <= 23 and 0 <= mm <= 59):
                raise ValueError("시간 형식이 올바르지 않습니다.")
            msg = m.group(4).strip()
            return ("weekly", wd, datetime.time(hh, mm, tzinfo=KST), msg)

        # 매주 요일 [시간 생략]
        m = re.match(r"^매주\s+([월화수목금토일](?:요일)?)\s+(.*)$", s)
        if m:
            wd = _KOR_WEEKDAY.get(m.group(1))
            if wd is None:
                raise ValueError("요일을 인식하지 못했습니다.")
            msg = m.group(2).strip()
            return ("weekly", wd, datetime.time(9, 0, tzinfo=KST), msg)

        raise ValueError("지원되는 패턴이 아닙니다. (예: '매일 09:00 오늘 일정', '매주 월요일 08:30 이번주 일정')")

    async def _send_custom_message(self, chat_id: int, message: str):
        """단순 커스텀 메시지 전송"""
        await self.sender.app.bot.send_message(chat_id=chat_id, text=message)

    async def schedule_custom(self, chat_id: int, text: str) -> str:
        """
        /remind 명령에서 호출:
          - '매일 HH:MM ...'
          - '매주 요일 HH:MM ...' or '매주 요일 ...'
        """
        if not self.app:
            raise ValueError("Application이 준비되지 않았습니다.")

        mode, weekday, t, msg = self._parse_remind_text(text)

        if mode == "daily":
            self.app.job_queue.run_daily(
                lambda ctx: self.app.create_task(self._send_custom_message(chat_id, msg)),
                time=t,
                name=f"daily:{chat_id}:{t.strftime('%H%M')}",
                chat_id=chat_id,
            )
            return f"매일 {t.strftime('%H:%M')} - '{msg}'"

        if mode == "weekly":
            # 첫 발생일(다음 해당 요일) 계산
            first_date = _next_weekday_date(datetime.datetime.now(tz=KST).date(), weekday)
            first_dt = datetime.datetime.combine(first_date, t).astimezone(KST)

            async def _weekly_send(ctx: CallbackContext):
                await self._send_custom_message(chat_id, msg)

            # 첫 실행 예약
            self.app.job_queue.run_once(
                lambda ctx: self.app.create_task(_weekly_send(ctx)),
                when=first_dt,
                name=f"weekly_once:{chat_id}:{weekday}:{t.strftime('%H%M')}",
            )
            # 이후 매주 반복
            self.app.job_queue.run_repeating(
                lambda ctx: self.app.create_task(_weekly_send(ctx)),
                interval=datetime.timedelta(days=7),
                first=first_dt + datetime.timedelta(days=7),
                name=f"weekly:{chat_id}:{weekday}:{t.strftime('%H%M')}",
                chat_id=chat_id,
            )
            wd_kor = [k for k, v in _KOR_WEEKDAY.items() if v == weekday and len(k) == 1][0]  # 월/화/...
            return f"매주 {wd_kor}요일 {t.strftime('%H:%M')} - '{msg}'"

        raise ValueError("알 수 없는 모드")

    # ------------------------------ 일정별 알림 ------------------------------

    async def schedule_for_schedule(self, user_id: int, schedule_row, offset_minutes: int):
        """
        일정건에 대한 알림 예약 + DB 저장
        schedule_row: (id, title, desc, date, time)
        offset_minutes: 0(정각), 30, 60, 1440(하루 전) 등
        """
        reminder_id = self.repo.add_reminder(user_id, schedule_row[0], offset_minutes)
        await self._schedule_one(user_id, schedule_row, offset_minutes, reminder_id)

    async def _schedule_one(self, user_id: int, schedule_row, offset_minutes: int, reminder_id: int):
        """
        하나의 알림을 실제 스케줄러에 등록
        - 시간 없으면 기본 09:00
        - 트리거 시간이 과거면 스킵
        """
        if not self.app:
            return

        sid, title, desc, dt_str, tm_str = schedule_row

        # 일정 시간 계산 (없으면 09:00)
        if tm_str:
            hh, mm = map(int, tm_str.split(":"))
        else:
            hh, mm = 9, 0

        event_dt = datetime.datetime.strptime(f"{dt_str} {hh:02d}:{mm:02d}", "%Y-%m-%d %H:%M")
        event_dt = event_dt.replace(tzinfo=KST)

        # 오프셋 적용
        fire_dt = event_dt - datetime.timedelta(minutes=offset_minutes)

        # 이미 지난 경우 스킵
        if fire_dt <= datetime.datetime.now(tz=KST):
            return

        name = f"reminder:{reminder_id}"

        async def _send(ctx: CallbackContext):
            tail = dday_text(dt_str, tz=KST)
            body = f"🔔 알림: {dt_str} {tm_str or ''} {title} {tail}"
            await self.sender.app.bot.send_message(chat_id=user_id, text=body)

        # 예약
        self.app.job_queue.run_once(
            lambda ctx: self.app.create_task(_send(ctx)),
            when=fire_dt,
            name=name,
            chat_id=user_id,
        )
