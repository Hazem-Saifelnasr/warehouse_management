# src/app/core/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # === App data ===
    APP_NAME: str
    APP_VERSION: str

    APP_HOST: str
    APP_PORT: int

    # === DataBase ===
    DATABASE_URL: str

    # === Secrets for Authentication ===
    # Secrets for JWT signing
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = "src/.env"


@lru_cache
def get_settings():
    return Settings()
