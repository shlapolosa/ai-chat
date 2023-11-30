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

# Dependency provider for OpenAIAssistantManager
def get_assistant_manager():
    return OpenAIAssistantManager(settings.openai_api_key)

# Dependency provider for ChatService
def get_chat_service(assistant_manager: OpenAIAssistantManager = Depends(get_assistant_manager)):
    return ChatService(assistant_manager)

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
    logger.info("Starting up...")
    assistant_manager = OpenAIAssistantManager(settings.openai_api_key)
    assistant_manager.load_or_create_assistants()
    logger.info("Assistants have been loaded.")
    print("Server is running. Access it at http://127.0.0.1:8000")  # Replace with actual host and port if known

# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Shutting down...")
