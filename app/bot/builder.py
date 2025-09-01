from telegram.ext import Application

class PTBSender:
    def __init__(self, app: Application):
        self.app = app

    async def send_daily(self, chat_id, date, items):
        if not items:
            await self.app.bot.send_message(chat_id, f"{date} 일정 없음")
        else:
            lines = [f"{date} 일정"]
            for sid,title,desc,dt,tm in items:
                lines.append(f"- [{sid}] {title} ({tm or '시간 미정'})")
            await self.app.bot.send_message(chat_id, "\n".join(lines))
