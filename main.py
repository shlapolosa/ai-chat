import logging
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
import sentry_sdk
import uvicorn

from api import router as api_router
from config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up Sentry if DSN is provided
if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN)

# Add Sentry middleware
app.add_middleware(SentryAsgiMiddleware)

# Include routers with a prefix
app.include_router(api_router, prefix="/api")

# Application startup event
@app.on_event("startup")
async def startup_event():
    logging.info("Starting up...")
    print("Server is running. Access it at http://127.0.0.1:8000")  # Replace with actual host and port if known

# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Shutting down...")
