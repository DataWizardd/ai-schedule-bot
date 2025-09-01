import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

class Settings:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "data/schedules.db"))

settings = Settings()
