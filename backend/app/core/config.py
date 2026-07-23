from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    DEBUG: bool = False

    MONGO_URL: str
    MONGO_DB_NAME: str = "url_shortener_db"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
        "http://localhost:4173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )


settings = Settings()
