# src/app/core/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # === App data ===
    APP_NAME: str
    APP_VERSION: str

    APP_HOST: str
    APP_PORT: int

    ENV: str
    # === DataBase ===
    # ------------- postgreSQL -------------
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    # POSTGRES_SYNC_PREFIX: str
    # POSTGRES_ASYNC_PREFIX: str
    # POSTGRES_URI: str
    # POSTGRES_URL: str

    # ------------- pgadmin -------------
    PGADMIN_DEFAULT_EMAIL: str
    PGADMIN_DEFAULT_PASSWORD: str
    PGADMIN_LISTEN_PORT: int

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
