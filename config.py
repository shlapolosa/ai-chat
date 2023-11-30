from pydantic_settings import BaseSettings

from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Application"
    SENTRY_DSN: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
