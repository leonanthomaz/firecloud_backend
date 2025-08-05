from typing import Optional
from pydantic import BaseModel

class ProductRequest(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    stock: Optional[int] = None
    image: Optional[str] = None
    company_id: int
    code: Optional[str] = None