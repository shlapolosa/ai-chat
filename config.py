from pydantic_settings import BaseSettings

from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Application"
    SENTRY_DSN: Optional[str] = None  # Replace with your Sentry DSN or leave as None

    class Config:
        env_file = ".env"

settings = Settings()
