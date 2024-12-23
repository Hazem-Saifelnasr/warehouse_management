# src/app/core/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # === App data ===
    APP_NAME: str
    APP_VERSION: str

    # === DataBase ===
    DATABASE_URL: str

    # === Secrets for Authentication ===
    # Secrets for JWT signing
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = "src/.env"


def get_settings():
    return Settings()
