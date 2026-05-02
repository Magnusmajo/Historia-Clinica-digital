import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./historia_clinica.db")
        self.frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
        self.app_timezone = os.getenv("APP_TIMEZONE", "America/Montevideo")
        self.api_key = os.getenv("APP_API_KEY", "dev-local-api-key")
        self.require_api_key = _get_bool("APP_REQUIRE_API_KEY", True)
        self.auto_create_tables = _get_bool("AUTO_CREATE_TABLES", True)
        self.google_calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        self.google_credentials_file = os.getenv(
            "GOOGLE_CREDENTIALS_FILE",
            "credentials.json",
        )
        self.google_token_file = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
        self.google_oauth_state_file = os.getenv(
            "GOOGLE_OAUTH_STATE_FILE",
            ".google_oauth_state",
        )
        self.google_redirect_uri = os.getenv(
            "GOOGLE_REDIRECT_URI",
            "http://localhost:8000/google-calendar/callback",
        )


@lru_cache
def get_settings():
    return Settings()
