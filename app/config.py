import os
from dataclasses import dataclass

@dataclass
class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/schedules.db")

settings = Settings()
