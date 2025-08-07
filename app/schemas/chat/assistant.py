from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.enums.assistant import AssistantStatus

class AssistantRequest(BaseModel):
    company_id: int
    status: Optional[str] = None
    assistant_link: Optional[str] = None
    assistant_name: Optional[str] = None
    assistant_api_url: Optional[str] = None
    assistant_api_key: Optional[str] = None
    assistant_type: Optional[str] = None
    assistant_model: Optional[str] = None
    ai_token: Optional[str] = None
    assistant_token_limit: Optional[int] = None
    assistant_token_usage: Optional[int] = 0
    assistant_token_reset_date: Optional[datetime] = None

class AssistantUpdate(BaseModel):
    status: Optional[str] = None
    assistant_link: Optional[str] = None
    assistant_name: Optional[str] = None
    assistant_api_url: Optional[str] = None
    assistant_api_key: Optional[str] = None
    assistant_type: Optional[str] = None
    assistant_model: Optional[str] = None
    ai_token: Optional[str] = None
    assistant_token_limit: Optional[int] = None
    assistant_token_usage: Optional[int] = None
    assistant_token_reset_date: Optional[datetime] = None

class AssistantResponse(AssistantRequest):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AssistantStatusUpdate(BaseModel):
    status: AssistantStatus