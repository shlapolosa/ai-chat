import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_name: str = os.getenv('PROJECT_NAME', 'Chat Application')
    openai_api_key: str = os.getenv('OPENAI_API_KEY')
    sentry_dsn: Optional[str] = os.getenv('SENTRY_DSN')
    database_url: Optional[str] = os.getenv('DATABASE_URL')
    environment: Optional[str] = os.getenv('ENVIRONMENT', 'development')
    backend_cors_origins: Optional[str] = os.getenv('BACKEND_CORS_ORIGINS', '*')

settings = Settings()
