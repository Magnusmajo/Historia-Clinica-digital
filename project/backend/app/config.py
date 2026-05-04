import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

DEV_API_KEY = "dev-local-api-key"
DEV_SECRET_KEY = "dev-local-secret-change-me"
DEV_ADMIN_PASSWORD = "Admin12345"


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} debe ser un numero entero") from exc


def _get_csv(name: str, default_values: list[str] | None = None) -> list[str]:
    values = default_values or []
    raw_value = os.getenv(name)
    if raw_value:
        values.extend(raw_value.split(","))

    normalized = []
    for value in values:
        value = value.strip().rstrip("/")
        if value and value not in normalized:
            normalized.append(value)
    return normalized


class Settings:
    def __init__(self):
        self.environment = os.getenv("APP_ENV", "development").strip().lower()
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./historia_clinica.db")
        self.frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
        self.frontend_origins = _get_csv("FRONTEND_ORIGINS", [self.frontend_origin])
        if self.environment not in {"production", "prod"}:
            self.frontend_origins = _get_csv(
                "FRONTEND_ORIGINS",
                [*self.frontend_origins, "http://127.0.0.1:5173"],
            )
        self.app_timezone = os.getenv("APP_TIMEZONE", "America/Montevideo")
        self.api_key = os.getenv("APP_API_KEY", DEV_API_KEY)
        self.require_api_key = _get_bool("APP_REQUIRE_API_KEY", True)
        self.secret_key = os.getenv("SECRET_KEY", DEV_SECRET_KEY)
        self.access_token_minutes = _get_int("ACCESS_TOKEN_MINUTES", 480)
        self.require_user_auth = _get_bool("APP_REQUIRE_USER_AUTH", True)
        self.seed_admin_user = _get_bool("SEED_ADMIN_USER", True)
        self.default_admin_name = os.getenv("DEFAULT_ADMIN_NAME", "Administrador")
        self.default_admin_email = os.getenv(
            "DEFAULT_ADMIN_EMAIL",
            "admin@elara.com",
        )
        self.default_admin_password = os.getenv(
            "DEFAULT_ADMIN_PASSWORD",
            DEV_ADMIN_PASSWORD,
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

    @property
    def is_production(self) -> bool:
        return self.environment in {"production", "prod"}

    def validate(self):
        if not self.is_production:
            return

        errors = []
        if self.require_api_key and self.api_key == DEV_API_KEY:
            errors.append("APP_API_KEY no puede usar el valor de desarrollo")
        if self.require_user_auth and (
            self.secret_key == DEV_SECRET_KEY or len(self.secret_key) < 32
        ):
            errors.append("SECRET_KEY debe ser unico y tener al menos 32 caracteres")
        if self.seed_admin_user and self.default_admin_password == DEV_ADMIN_PASSWORD:
            errors.append("DEFAULT_ADMIN_PASSWORD no puede usar el valor de desarrollo")
        if self.auto_create_tables:
            errors.append("AUTO_CREATE_TABLES debe ser false en produccion")

        if errors:
            raise RuntimeError("Configuracion insegura: " + "; ".join(errors))


@lru_cache
def get_settings():
    return Settings()
