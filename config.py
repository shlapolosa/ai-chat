from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Application"
    SENTRY_DSN: str = None  # Replace with your Sentry DSN or leave as None

    class Config:
        env_file = ".env"

settings = Settings()
