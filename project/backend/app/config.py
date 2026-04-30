import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    database_url = os.getenv("DATABASE_URL", "sqlite:///./historia_clinica.db")
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    google_calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    google_credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    google_token_file = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
    google_redirect_uri = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:8000/google-calendar/callback",
    )
    app_timezone = os.getenv("APP_TIMEZONE", "America/Montevideo")


@lru_cache
def get_settings():
    return Settings()
