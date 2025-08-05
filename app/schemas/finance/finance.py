from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class FinanceBase(BaseModel):
    amount: float
    type: Literal["revenue", "expense"]
    description: Optional[str] = None
    category_id: Optional[int] = None
    related_company_id: Optional[int] = None
    related_payment_id: Optional[int] = None

class FinanceCreate(FinanceBase):
    pass

class FinanceUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[Literal["revenue", "expense"]] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    related_company_id: Optional[int] = None
    related_payment_id: Optional[int] = None

class FinanceRead(FinanceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
