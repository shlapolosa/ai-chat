from typing import Optional
from typing import List
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


class RootResponse(BaseModel):
    loaded_assistants: List[dict]
    environment_variables: dict
