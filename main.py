import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

# Configure structured logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
import sentry_sdk
import uvicorn

from api import router as api_router
from fastapi import Depends
from config import settings
from openai_assistant_manager import OpenAIAssistantManager
from chat_service import ChatService

app = FastAPI(title=settings.PROJECT_NAME)

# Create a global instance of ChatService
chat_service_instance = ChatService(OpenAIAssistantManager(settings.openai_api_key))

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
    assistant_manager.load_or_create_assistants()
    chat_service_instance = ChatService(assistant_manager)
    logger.info("Assistants have been loaded.")
    print("Server is running. Access it at http://127.0.0.1:8000")  # Replace with actual host and port if known

# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Shutting down...")
