# app/main.py
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from app.config import settings
from app.storage.db import DB
from app.storage.schedule_repo import ScheduleRepo
from app.services.kdate_parser import KDateParser
from app.services.ai_client import AIClient
from app.services.ai_schedule_parser import AIScheduleParser
from app.services.reminder import ReminderService
from app.bot.handlers import Handlers
from app.bot.builder import PTBSender

def setup_logging():
    logging.basicConfig(format="%(asctime)s %(levelname)s [%(name)s] %(message)s", level=logging.INFO)

def main():
    setup_logging()
    app = ApplicationBuilder().token(settings.BOT_TOKEN).build()

    db = DB(settings.DATABASE_PATH)
    repo = ScheduleRepo(db)
    kparser = KDateParser()
    ai_client = AIClient(settings.OPENAI_API_KEY)
    ai = AIScheduleParser(ai_client, kparser)

    sender = PTBSender(app)
    reminder = ReminderService(repo, sender)
    reminder.setup(app)

    handlers = Handlers(repo=repo, ai=ai, kparser=kparser, reminder=reminder)

    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("menu", handlers.menu))
    app.add_handler(CommandHandler("add", handlers.add))
    app.add_handler(CommandHandler("list", handlers.list_all))
    app.add_handler(CommandHandler("today", handlers.today))
    app.add_handler(CommandHandler("delete", handlers.delete))
    app.add_handler(CommandHandler("delete_all", handlers.delete_all))
    app.add_handler(CommandHandler("remind", handlers.remind))
    app.add_handler(CallbackQueryHandler(handlers.on_callback))
    app.add_handler(CommandHandler("reminders", handlers.reminders))

    print("🤖 AI 기반 일정 관리 봇 시작")
    app.run_polling(allowed_updates=[])

if __name__ == "__main__":
    main()
