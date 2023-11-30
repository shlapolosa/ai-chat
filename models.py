from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class AssistantInfo(BaseModel):
    assistant_name: str
    assistant_id: str

class EnvironmentVariables(BaseModel):
    key: str
    value: str

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

class DetailsResponse(BaseModel):
    loaded_assistants: List[AssistantInfo] = Field(default_factory=list)
    environment_variables: List[EnvironmentVariables] = Field(default_factory=list)
