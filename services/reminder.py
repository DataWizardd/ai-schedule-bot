import pendulum
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Sequence
from app.storage.schedule_repo import ScheduleRepo
from app.services.timeutil import now_kst
from app.bot.builder import BotSender

class ReminderService:
    def __init__(self, repo: ScheduleRepo, sender: BotSender, tz: str = "Asia/Seoul"):
        self.repo = repo
        self.sender = sender
        self.tz = tz
        self.scheduler = AsyncIOScheduler(timezone=tz)

    def start(self):
        # 매일 09:00 오늘 일정 알림
        self.scheduler.add_job(self.send_today, "cron", hour=9, minute=0, id="daily_today")
        # 매일 20:00 내일 일정 미리 알림
        self.scheduler.add_job(self.send_tomorrow, "cron", hour=20, minute=0, id="daily_tomorrow")
        self.scheduler.start()

    async def send_today(self):
        user_ids = self.repo.list_user_ids()
        today = now_kst().to_date_string()
        for uid in user_ids:
            items = self.repo.get_by_date(uid, today)
            await self.sender.send_daily(uid, today, items)

    async def send_tomorrow(self):
        user_ids = self.repo.list_user_ids()
        tomorrow = now_kst().add(days=1).to_date_string()
        for uid in user_ids:
            items = self.repo.get_by_date(uid, tomorrow)
            await self.sender.send_tomorrow(uid, tomorrow, items)
