import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
DATABASE_URL = settings.database_url

connect_args = {}
engine_args = {
    "pool_pre_ping": True,
    "pool_recycle": settings.pool_recycle,
}

if settings.is_postgres:
    connect_args = {
        "connect_timeout": settings.connect_timeout,
        "options": f"-c statement_timeout={settings.statement_timeout_ms}",
    }
    engine_args.update(
        {
            "pool_size": settings.pool_size,
            "max_overflow": settings.max_overflow,
            "pool_timeout": settings.pool_timeout,
        }
    )
elif settings.is_test and DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
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
