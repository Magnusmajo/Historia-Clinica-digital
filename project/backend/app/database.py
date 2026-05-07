import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
DATABASE_URL = settings.database_url

engine_args = {
    "pool_pre_ping": True,
    "pool_recycle": settings.pool_recycle,
    "pool_timeout": settings.pool_timeout,
    "pool_size": settings.pool_size,
    "max_overflow": settings.max_overflow,
    "pool_use_lifo": True,
    "hide_parameters": True,
}

if settings.is_postgres:
    options = [
        f"-c statement_timeout={settings.statement_timeout_ms}",
        "-c idle_in_transaction_session_timeout=30000",
    ]
    if settings.db_schema:
        options.append(f"-c search_path={settings.db_schema}")
    connect_args = {
        "connect_timeout": settings.connect_timeout,
        "options": " ".join(options),
        "application_name": "historia_clinica_digital",
    }
else:
    raise RuntimeError("DATABASE_URL debe usar PostgreSQL")

logger.info("Configurando base de datos %s", settings.safe_database_url)
engine = create_engine(DATABASE_URL, connect_args=connect_args, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_database():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
