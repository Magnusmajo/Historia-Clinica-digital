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
        self.secret_key = os.getenv("SECRET_KEY", "dev-local-secret-change-me")
        self.access_token_minutes = int(os.getenv("ACCESS_TOKEN_MINUTES", "480"))
        self.require_user_auth = _get_bool("APP_REQUIRE_USER_AUTH", True)
        self.seed_admin_user = _get_bool("SEED_ADMIN_USER", True)
        self.default_admin_name = os.getenv("DEFAULT_ADMIN_NAME", "Administrador")
        self.default_admin_email = os.getenv(
            "DEFAULT_ADMIN_EMAIL",
            "admin@elara.com",
        )
        self.default_admin_password = os.getenv(
            "DEFAULT_ADMIN_PASSWORD",
            "Admin12345",
        )
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
