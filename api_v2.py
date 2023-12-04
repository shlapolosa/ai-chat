import fastapi
from fastapi import APIRouter, Depends, Form, HTTPException, Body, Response
from typing import Optional
from pydantic import parse_obj_as
from main import logger
from chat_service import ChatService
from models import ChatRequest, ChatResponse
from nedbank_api import write_cache, read_cache, make_payment_function, token_light
from openai_assistant_manager import OpenAIAssistantManager
from config import settings
import os
import re

from fastapi import APIRouter

router = APIRouter()

assistant_manager = OpenAIAssistantManager(settings.openai_api_key)
logger.info("Assistants have been loaded.")
chat_service_instance = ChatService(assistant_manager)
logger.info("ChatService have been loaded.")

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
    # env_vars = {key: os.getenv(key) for key in os.environ.keys()}
    # masked_env_vars = mask_sensitive_info(settings)
    return {
        "loaded_assistants": loaded_assistants,
        "configuration": {
            "OPEN_API_KEY": settings.openai_api_key,
            "AIRTABLE_API_KEY": settings.airtable_api_key,
            "PROJECT_NAME": settings.PROJECT_NAME,
            "SENTRY_DSN": settings.SENTRY_DSN,
            "DATABASE_URL": settings.database_url,
            "ENVIRONMENT": settings.environment,
            "BACKEND_CORS_ORIGINS": settings.backend_cors_origins
        }
    }

@router.get("/chat", response_model=ChatResponse)
async def check_run_status(thread_id: str, run_id: str):
    """
    GET endpoint to check the status of a chat run using query parameters. Accepts the thread ID and run ID as query parameters,
    and returns the status of the run along with any response message.
    """
    logger.info(f"check_run_status: Received chat request with thread_id={thread_id} and run_id={run_id}")
    try:
        message_content, status = await chat_service_instance.check_run_status(thread_id, run_id)
        return ChatResponse(thread_id=thread_id, run_id=run_id, message=message_content, status=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import File, UploadFile

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    file: UploadFile = File(...),
    assistant_name: Optional[str] = Form(None),
    thread_id: str = Form(...),
    message: str = Form(...)
):
    """
    POST method to handle a chat message and an optional file. This endpoint accepts a ChatRequest object
    and an optional file, processes it using the ChatService, and returns the response.
    """
    # file_content = await file.read()

    chat_request = ChatRequest(
        assistant_name=assistant_name,
        thread_id=thread_id,
        message=message
    )
 
    logger.info(f"chat_endpoint: Received chat request with values={chat_request}")

    if file:
        # Here you can add logic to handle the file, e.g., save it or process it.
        logger.info(f"Received file with filename: {file.filename} of size {file.size}")
    try:
        run_id = await chat_service_instance.handle_chat(
            assistant_name=chat_request.assistant_name,
            thread_id=chat_request.thread_id,
            user_input=chat_request.message,
            file=file  # Pass the optional file to the handle_chat method
        )
        response = ChatResponse(run_id=run_id)
        logger.info(f"chat_endpoint: Completed handling chat request with run_id={run_id}")
        return response
    except Exception as e:
        logger.error(f"chat_endpoint: Error handling chat request - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/chat", response_model=ChatResponse)
async def start_chat(
    assistant_name: str = None
):
    """
    Endpoint to handle a chat message. This endpoint accepts an assistant_name parameter,
    starts a new conversation thread, and returns the thread ID.
    """
    thread_id = await chat_service_instance.start_thread(assistant_name)
    return ChatResponse(thread_id=thread_id)


import json

@router.get("/getOAuthCode")
def oauth_callback(code, state):
    from nedbank_api import token_heavy, make_payment_function, write_cache, read_cache
    if code:
        if state == "payment-request":
            token_response = token_heavy(code)
            access_token = token_response.get("access_token")
            write_cache('payment_refresh_token', token_response.get("refresh_token"))
            write_cache('payment_access_token', token_response.get("access_token"))
            amount = read_cache('payment_amount')
            consent_id = read_cache('payment_consent_id')
            make_payment_function(amount, consent_id, access_token)
        else:
            token_response = token_heavy(code)
            write_cache('refresh_token', token_response.get("refresh_token"))
            write_cache('access_token', token_response.get("access_token"))
        # request.session.set_expiry(token_response.get("expires_id"))
        return {'status': 'ok'}
    return ''
    # return
    #     'error': request.GET.get('error'),
    #     'error_description': request.GET.get('error_description'),
    # })

