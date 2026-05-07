import logging
import time

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine
from app.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


def main():
    deadline = time.monotonic() + 60
    while True:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Base de datos disponible")
            return
        except SQLAlchemyError as exc:
            if time.monotonic() >= deadline:
                raise RuntimeError("La base de datos no estuvo disponible a tiempo") from exc
            logger.info("Esperando base de datos...")
            time.sleep(2)


if __name__ == "__main__":
    main()
