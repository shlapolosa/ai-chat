from fastapi import APIRouter, Depends
from fastapi import APIRouter, Depends, HTTPException, Body
from .services.chat_service import ChatService
from .models import ChatRequest, ChatResponse

router = APIRouter()

@router.get("/")
async def read_root():
    return {"Hello": "World"}

@router.put("/chat")
async def start_conversation(chat_service: ChatService = Depends(), platform: str = "Not Specified"):
    """
    Endpoint to start a new conversation thread. The 'platform' parameter can be used
    to specify the type of assistant or conversation context.
    """
    thread_id = await chat_service.start_thread(platform)
    return {"thread_id": thread_id}

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    action: str = Body(..., embed=True),
    thread_id: str = Body(..., embed=True),
    user_input: str = Body(..., embed=True),
    chat_service: ChatService = Depends()
):
    """
    Endpoint to handle a chat message. This endpoint accepts an action, thread ID, 
    and the user's input message, processes it using the ChatService, and returns 
    the response.
    """
    if not thread_id:
        raise HTTPException(status_code=400, detail="Missing thread_id in the request")

    try:
        run_id = await chat_service.handle_chat(action, thread_id, user_input)
        return ChatResponse(response=run_id)  # Adjusted to match the ChatResponse model
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    """
    Endpoint to start a new conversation thread. The 'platform' parameter can be used
    to specify the type of assistant or conversation context.
    """
    thread_id = await chat_service.start_thread(platform)
    return {"thread_id": thread_id}
