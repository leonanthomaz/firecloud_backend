from pydantic import BaseModel
from typing import Optional

class CategoryRequest(BaseModel):
    name: str
    description: Optional[str] = None
    company_id: int

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None