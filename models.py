from pydantic import BaseModel

class ChatRequest(BaseModel):
    """
    Defines the structure of the chat request data.
    """
    message: str
    # You can add more fields if needed, like 'user_id', 'session_id', etc.

class ChatResponse(BaseModel):
    """
    Defines the structure of the chat response data.
    """
    thread_id: Optional[str] = None
    run_id: Optional[str] = None
    message: Optional[str] = None
    status: Optional[str] = None

class CheckRunRequest(BaseModel):
    """
    Defines the structure for checking the status of a conversation run.
    """
    thread_id: str
    run_id: str
    # Additional fields can be included as per your application's requirements.

class CheckRunResponse(BaseModel):
    """
    Defines the structure of the response for a check run request.
    """
    status: str
    response: str  # This might contain the message or relevant information about the run status.
    # Additional response details can be added.
