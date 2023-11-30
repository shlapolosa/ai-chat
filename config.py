import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = os.getenv('OPENAI_API_KEY')
    sentry_dsn: str = os.getenv('SENTRY_DSN')
    database_url: str = os.getenv('DATABASE_URL')
    environment: str = os.getenv('ENVIRONMENT')
    backend_cors_origins: str = os.getenv('BACKEND_CORS_ORIGINS')

settings = Settings()
