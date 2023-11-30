from fastapi import APIRouter, Depends, HTTPException, Body
from services.chat_service import ChatService
from .models import ChatRequest, ChatResponse, CheckRunRequest, CheckRunResponse

router = APIRouter()

@router.get("/api/")
async def read_root():
    return {"Hello": "World"}

@router.get("/api/chat", response_model=ChatResponse)
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

@router.post("/api/chat", response_model=ChatResponse)
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

@router.put("/api/chat", response_model=ChatResponse)
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
