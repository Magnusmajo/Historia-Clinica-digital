import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    database_url = os.getenv("DATABASE_URL", "sqlite:///./historia_clinica.db")
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


@lru_cache
def get_settings():
    return Settings()
