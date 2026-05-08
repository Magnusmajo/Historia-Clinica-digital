import os
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BASE_DIR.parent

SAFE_LOCAL_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost",
    "http://127.0.0.1",
)
POSTGRES_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,62}$")


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int, *, minimum: int | None = None) -> int:
    value = os.getenv(name)
    if value is None:
        parsed = default
    else:
        try:
            parsed = int(value)
        except ValueError as exc:
            raise RuntimeError(f"{name} debe ser un numero entero") from exc
    if minimum is not None and parsed < minimum:
        raise RuntimeError(f"{name} debe ser mayor o igual a {minimum}")
    return parsed


def _get_csv(name: str, default_values: list[str] | tuple[str, ...] = ()) -> list[str]:
    values = list(default_values)
    raw_value = os.getenv(name)
    if raw_value:
        values.extend(raw_value.split(","))

    normalized = []
    for value in values:
        value = value.strip().rstrip("/")
        if value and value not in normalized:
            normalized.append(value)
    return normalized


def _resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_DIR / path


def _mask_url(value: str) -> str:
    parts = urlsplit(value)
    if not parts.password:
        return value
    username = parts.username or ""
    host = parts.hostname or ""
    port = f":{parts.port}" if parts.port else ""
    netloc = f"{username}:***@{host}{port}"
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


class Settings:
    def __init__(self):
        self.environment = os.getenv("APP_ENV", "development").strip().lower()
        self.database_url = os.getenv("DATABASE_URL", "").strip()
        self.frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
        self.frontend_origins = _get_csv("FRONTEND_ORIGINS", [self.frontend_origin])
        if not self.is_production:
            self.frontend_origins = _get_csv(
                "FRONTEND_ORIGINS",
                [*self.frontend_origins, *SAFE_LOCAL_ORIGINS],
            )
        self.allowed_hosts = _get_csv(
            "ALLOWED_HOSTS",
            ["localhost", "127.0.0.1", "testserver"] if not self.is_production else (),
        )
        self.trust_proxy_headers = _get_bool("TRUST_PROXY_HEADERS", self.is_production)
        self.app_timezone = os.getenv("APP_TIMEZONE", "America/Montevideo")
        self.api_key = os.getenv("APP_API_KEY", "")
        self.require_api_key = _get_bool("APP_REQUIRE_API_KEY", True)
        self.secret_key = os.getenv("SECRET_KEY", "")
        self.access_token_minutes = _get_int("ACCESS_TOKEN_MINUTES", 30, minimum=5)
        self.refresh_token_days = _get_int("REFRESH_TOKEN_DAYS", 14, minimum=1)
        self.require_user_auth = _get_bool("APP_REQUIRE_USER_AUTH", True)
        self.seed_admin_user = _get_bool("SEED_ADMIN_USER", False)
        self.default_admin_name = os.getenv("DEFAULT_ADMIN_NAME", "Administrador")
        self.default_admin_email = os.getenv(
            "DEFAULT_ADMIN_EMAIL",
            "admin@elara.com",
        )
        self.default_admin_password = os.getenv(
            "DEFAULT_ADMIN_PASSWORD",
            "",
        )
        self.auto_create_tables = _get_bool("AUTO_CREATE_TABLES", False)
        self.upload_dir = _resolve_path(os.getenv("UPLOAD_DIR", "uploads"))
        self.max_upload_mb = _get_int("MAX_UPLOAD_MB", 12, minimum=1)
        self.docs_enabled = _get_bool("ENABLE_API_DOCS", not self.is_production)
        self.google_calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        self.google_credentials_file = str(
            _resolve_path(os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json"))
        )
        self.google_token_file = str(
            _resolve_path(os.getenv("GOOGLE_TOKEN_FILE", "token.json"))
        )
        self.google_oauth_state_file = str(
            _resolve_path(os.getenv("GOOGLE_OAUTH_STATE_FILE", ".google_oauth_state"))
        )
        self.google_redirect_uri = os.getenv(
            "GOOGLE_REDIRECT_URI",
            "http://localhost:8000/google-calendar/callback",
        )
        self.cookie_secure = _get_bool("COOKIE_SECURE", self.is_production)
        self.cookie_samesite = os.getenv("COOKIE_SAMESITE", "lax").strip().lower()
        self.cookie_domain = os.getenv("COOKIE_DOMAIN") or None
        self.access_cookie_name = os.getenv("ACCESS_COOKIE_NAME", "hcd_access")
        self.refresh_cookie_name = os.getenv("REFRESH_COOKIE_NAME", "hcd_refresh")
        self.csrf_cookie_name = os.getenv("CSRF_COOKIE_NAME", "hcd_csrf")
        self.rate_limit_enabled = _get_bool("RATE_LIMIT_ENABLED", True)
        self.redis_url = os.getenv("REDIS_URL", "").strip() or None
        self.rate_limit_requests = _get_int("RATE_LIMIT_REQUESTS", 240, minimum=1)
        self.rate_limit_window_seconds = _get_int(
            "RATE_LIMIT_WINDOW_SECONDS",
            60,
            minimum=1,
        )
        self.auth_rate_limit_requests = _get_int(
            "AUTH_RATE_LIMIT_REQUESTS",
            12,
            minimum=1,
        )
        self.pool_size = _get_int("DB_POOL_SIZE", 10, minimum=1)
        self.max_overflow = _get_int("DB_MAX_OVERFLOW", 20, minimum=0)
        self.pool_recycle = _get_int("DB_POOL_RECYCLE_SECONDS", 1800, minimum=30)
        self.pool_timeout = _get_int("DB_POOL_TIMEOUT_SECONDS", 10, minimum=1)
        self.statement_timeout_ms = _get_int(
            "DB_STATEMENT_TIMEOUT_MS",
            30000,
            minimum=1000,
        )
        self.connect_timeout = _get_int("DB_CONNECT_TIMEOUT_SECONDS", 5, minimum=1)
        self.db_schema = os.getenv("DB_SCHEMA", "").strip() or None
        self.log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()

    @property
    def is_production(self) -> bool:
        return self.environment in {"production", "prod"}

    @property
    def is_test(self) -> bool:
        return self.environment in {"test", "testing"}

    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith(("postgres://", "postgresql://", "postgresql+psycopg2://"))

    @property
    def safe_database_url(self) -> str:
        return _mask_url(self.database_url)

    def validate(self):
        errors = []

        if not self.database_url:
            errors.append("DATABASE_URL es obligatorio")
        elif not self.is_postgres:
            errors.append("DATABASE_URL debe usar PostgreSQL")
        if self.cookie_samesite not in {"lax", "strict", "none"}:
            errors.append("COOKIE_SAMESITE debe ser lax, strict o none")
        if self.cookie_samesite == "none" and not self.cookie_secure:
            errors.append("COOKIE_SECURE debe ser true cuando COOKIE_SAMESITE=none")
        if self.require_api_key and not self.api_key:
            errors.append("APP_API_KEY es obligatorio")
        if self.is_production and not self.require_api_key:
            errors.append("APP_REQUIRE_API_KEY debe ser true en produccion")
        if self.require_api_key and len(self.api_key) < 24 and self.is_production:
            errors.append("APP_API_KEY debe tener al menos 24 caracteres en produccion")
        if self.require_user_auth and len(self.secret_key) < 32:
            errors.append("SECRET_KEY debe ser unico y tener al menos 32 caracteres")
        if self.seed_admin_user and len(self.default_admin_password) < 12:
            errors.append("DEFAULT_ADMIN_PASSWORD debe tener al menos 12 caracteres")
        if self.auto_create_tables and self.is_production:
            errors.append("AUTO_CREATE_TABLES debe ser false en produccion")
        if self.is_production:
            if not self.allowed_hosts:
                errors.append("ALLOWED_HOSTS es obligatorio en produccion")
            if self.docs_enabled:
                errors.append("ENABLE_API_DOCS debe ser false en produccion")
        if self.db_schema and not POSTGRES_IDENTIFIER_PATTERN.fullmatch(self.db_schema):
            errors.append("DB_SCHEMA debe ser un identificador PostgreSQL valido")

        if errors:
            raise RuntimeError("Configuracion insegura: " + "; ".join(errors))


@lru_cache
def get_settings():
    return Settings()
