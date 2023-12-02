import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv('PROJECT_NAME', 'Chat Application')
    openai_api_key: str = os.getenv('OPENAI_API_KEY')
    airtable_api_key: str = os.getenv('AIRTABLE_API_KEY', 'your_default_airtable_api_key')
    SENTRY_DSN: str = os.getenv('SENTRY_DSN')
    database_url: Optional[str] = os.getenv('DATABASE_URL')
    environment: Optional[str] = os.getenv('ENVIRONMENT', 'development')
    backend_cors_origins: Optional[str] = os.getenv('BACKEND_CORS_ORIGINS', '*')

    NB_CLIENT_SECRET: Optional[str] = os.getenv('NB_CLIENT_SECRET')
    NB_FINANCIAL_ID: Optional[str] = os.getenv('NB_FINANCIAL_ID')
    NB_REDIRECT_URL: Optional[str] = os.getenv('NB_REDIRECT_URL')

settings = Settings()
