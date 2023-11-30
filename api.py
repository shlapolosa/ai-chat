from fastapi import APIRouter, Depends, HTTPException, Body, Response
from main import logger, chat_service_instance
from chat_service import ChatService
from models import ChatRequest, ChatResponse
from openai_assistant_manager import OpenAIAssistantManager
from config import settings
import os
import re

router = APIRouter()

def mask_sensitive_info(env_vars):
    sensitive_keys = ['API_KEY', 'DSN', 'DATABASE_URL', 'SECRET', 'PASSWORD']
    masked_env_vars = {}
    for key, value in env_vars.items():
        if any(sensitive_key in key for sensitive_key in sensitive_keys):
            masked_env_vars[key] = '*****'
        else:
            masked_env_vars[key] = value
    return masked_env_vars

@router.get("/")
async def read_root():
    logger.info("Root endpoint was called")
    loaded_assistants = chat_service_instance.get_loaded_assistants_info()
    env_vars = {key: os.getenv(key) for key in os.environ.keys()}
    masked_env_vars = mask_sensitive_info(env_vars)
    return {
        "loaded_assistants": loaded_assistants,
        "environment_variables": masked_env_vars
    }

@router.get("/chat", response_model=ChatResponse)
async def check_run_status(
    thread_id: str, run_id: str, chat_service: ChatService = Depends()
):
    """
    GET endpoint to check the status of a chat run using query parameters. Accepts the thread ID and run ID as query parameters,
    and returns the status of the run along with any response message.
    """
    try:
        message_content, status = await chat_service.check_run_status(thread_id, run_id)
        return ChatResponse(thread_id=thread_id, run_id=run_id, message=message_content, status=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    chat_request: ChatRequest,
    chat_service: ChatService = Depends()
):
    """
    POST method to handle a chat message. This endpoint accepts a ChatRequest object,
    processes it using the ChatService, and returns the response.
    """
    try:
        run_id = await chat_service.handle_chat(
            action=chat_request.action,
            thread_id=chat_request.thread_id,
            user_input=chat_request.message
        )
        return ChatResponse(response=run_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/chat", response_model=ChatResponse)
async def start_chat(
    platform: str,
    chat_service: ChatService = Depends()
):
    """
    Endpoint to handle a chat message. This endpoint accepts a platform parameter,
    starts a new conversation thread, and returns the thread ID.
    """
    thread_id = await chat_service.start_thread(platform)
    return ChatResponse(thread_id=thread_id)
