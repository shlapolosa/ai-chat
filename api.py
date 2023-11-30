from fastapi import APIRouter, Depends, HTTPException, Body
from .services.chat_service import ChatService
from .models import ChatRequest, ChatResponse, CheckRunRequest, CheckRunResponse

router = APIRouter()

@router.get("/")
async def read_root():
    return {"Hello": "World"}

@router.post("/check", response_model=CheckRunResponse)
async def check_run_status(
    check_request: CheckRunRequest,
    chat_service: ChatService = Depends()
):
    """
    Endpoint to check the status of a chat run. Accepts the thread ID and run ID,
    and returns the status of the run along with any response message.
    """
    try:
        message_content, status = await chat_service.check_run_status(
            thread_id=check_request.thread_id,
            run_id=check_request.run_id
        )
        return CheckRunResponse(response=message_content, status=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/chat", response_model=ChatResponse)
async def chat_endpoint(
    chat_request: ChatRequest,
    chat_service: ChatService = Depends()
):
    """
    Endpoint to handle a chat message. This endpoint accepts a ChatRequest object,
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

@router.post("/start", response_model=dict)
async def start_chat(
    platform: str,
    chat_service: ChatService = Depends()
):
    """
    Endpoint to start a new conversation thread. The 'platform' parameter can be used
    to specify the type of assistant or conversation context.
    """
    thread_id = await chat_service.start_thread(platform)
    return {"thread_id": thread_id}
