from typing import Protocol, List, Tuple, Optional
from telegram.ext import Application

# 스케줄 행: (id, title, description, date, time)
ScheduleRow = Tuple[int, str, str, str, Optional[str]]

class BotSender(Protocol):
    async def send_daily(self, chat_id: int, date: str, items: List[ScheduleRow]) -> None: ...
    async def send_tomorrow(self, chat_id: int, date: str, items: List[ScheduleRow]) -> None: ...

class PTBSender:
    def __init__(self, app: Application):
        self.app = app

    async def send_daily(self, chat_id: int, date: str, items: List[ScheduleRow]) -> None:
        if items:
            lines = [f"{date} 일정"]
            for sid, title, desc, dt, tm in items:
                t = tm if tm else "시간 미정"
                lines.append(f"- [{sid}] {title} ({t})")
            await self.app.bot.send_message(chat_id=chat_id, text="\n".join(lines))
        else:
            await self.app.bot.send_message(chat_id=chat_id, text=f"{date} 일정 없음")

    async def send_tomorrow(self, chat_id: int, date: str, items: List[ScheduleRow]) -> None:
        # 동일 포맷
        await self.send_daily(chat_id, date, items)
