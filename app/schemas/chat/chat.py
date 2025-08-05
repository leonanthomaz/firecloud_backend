

from datetime import datetime, timezone
from typing import Dict, List, Optional, Union

from pydantic import BaseModel
from sqlmodel import Field

from app.schemas.product.product import ProductRequest

class MessageRequest(BaseModel):
    message: str

class ChatRequest(BaseModel):
    message: str
    chat_code: Optional[str] = None
    whatsapp_id: Optional[str] = None
     
class ChatInteractionModel(BaseModel):
    company_id: int
    client_name: Optional[str] = None
    client_contact: Optional[str] = None
    outcome: Optional[str] = None
    interest: Optional[str] = None
    interaction_summary: Optional[str] = None
    estimated_value: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
class MessageRequest(BaseModel):
    message: str
    itens: List[ProductRequest]
    empresa_dados: Dict[str, Union[str, List[str]]]