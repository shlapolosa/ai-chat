import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from typing import Optional

# Configure structured logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
import sentry_sdk
import uvicorn

from api import router as api_router
from config import settings
from openai_assistant_manager import OpenAIAssistantManager
from chat_service import ChatService


chat_service_instance =Optional[ChatService]

app = FastAPI(title=settings.PROJECT_NAME)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins.split(","),  # Use the configured origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handler example
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

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
    global chat_service_instance
    logger.info("Starting up...")
    assistant_manager = OpenAIAssistantManager(settings.openai_api_key)
    logger.info("Assistants have been loaded.")
    chat_service_instance = ChatService(assistant_manager)
    logger.info("ChatService have been loaded.")

    print("Server is running. Access it at http://127.0.0.1:8000")  # Replace with actual host and port if known

# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Shutting down...")
