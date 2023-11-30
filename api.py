from fastapi import APIRouter, Depends
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
