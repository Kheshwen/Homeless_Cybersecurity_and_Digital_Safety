import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

# Project root /data folder (seed CSV/JSON files live here)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class Settings(BaseSettings):
    # LLM
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Twilio WhatsApp
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "")

    # Database (falls back to local SQLite if not set or still the placeholder)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./scamguard.db")


settings = Settings()
if "your-database-url" in settings.DATABASE_URL:
    settings.DATABASE_URL = "sqlite:///./scamguard.db"
