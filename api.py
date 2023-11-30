from fastapi import APIRouter, Depends
from .services.chat_service import ChatService

router = APIRouter()

@router.get("/start")
async def start_conversation(chat_service: ChatService = Depends(), platform: str = "Not Specified"):
    """
    Endpoint to start a new conversation thread. The 'platform' parameter can be used
    to specify the type of assistant or conversation context.
    """
    thread_id = await chat_service.start_thread(platform)
    return {"thread_id": thread_id}
