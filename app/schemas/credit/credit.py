from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CreditBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None
    origin: str  # 'plan' | 'package' | 'bonus' | 'payment'
    features: Optional[dict] = None
    token_amount: int
    price: float

class CreditCreate(CreditBase):
    company_id: int
    plan_id: Optional[int] = None

class CreditUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None
    origin: Optional[str] = None
    features: Optional[dict] = None
    token_amount: Optional[int] = None
    price: Optional[float] = None
    plan_id: Optional[int] = None

class CreditRead(CreditBase):
    id: int
    company_id: int
    plan_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
