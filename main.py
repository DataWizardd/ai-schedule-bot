import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from app.config import settings
from app.storage.db import DB
from app.storage.schedule_repo import ScheduleRepo
from app.services.kdate_parser import KDateParser
from app.services.ai_client import AIClient
from app.services.ai_schedule_parser import AIScheduleParser
from app.services.reminder import ReminderService
from app.services.cache import SuggestionCache
from app.bot.builder import PTBSender
from app.bot.handlers import Handlers

def setup_logging():
    logging.basicConfig(
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        level=logging.INFO,
    )

def main():
    load_dotenv()
    setup_logging()

    app = Application.builder().token(settings.BOT_TOKEN).build()

    db = DB(settings.DATABASE_PATH)
    repo = ScheduleRepo(db)
    kparser = KDateParser()
    ai_client = AIClient(settings.OPENAI_API_KEY)
    ai = AIScheduleParser(ai_client, kparser)
    cache = SuggestionCache(ttl_sec=600)

    handlers = Handlers(repo=repo, ai=ai, cache=cache)
    sender = PTBSender(app)
    reminder = ReminderService(repo=repo, sender=sender)
    reminder.start()

    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("help", handlers.start))
    app.add_handler(CommandHandler("add", handlers.add))
    app.add_handler(CommandHandler("add_ai", handlers.add_ai))
    app.add_handler(CommandHandler("list", handlers.list_all))
    app.add_handler(CommandHandler("today", handlers.today))
    app.add_handler(CommandHandler("delete", handlers.delete))
    app.add_handler(CommandHandler("suggest", handlers.suggest))
    app.add_handler(CommandHandler("analyze", handlers.analyze))
    app.add_handler(CallbackQueryHandler(handlers.on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.fyi))

    print("AI 기반 텔레그램 일정 관리 봇 시작")
    app.run_polling(allowed_updates=[])

if __name__ == "__main__":
    main()
