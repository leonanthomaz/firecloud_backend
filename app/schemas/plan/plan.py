from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class PlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    token_amount: Optional[int]
    features: Optional[dict] = None
    status: Optional[str] = None
    interval: Optional[str] = None
    interval_count: Optional[int] = None
    trial_period_days: Optional[int] = None
    max_users: Optional[int] = None
    max_storage: Optional[int] = None
    max_api_calls: Optional[int] = None
    slug: Optional[str] = None

class PlanCreate(PlanBase):
    pass

class PlanRequest(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    price: float
    token_amount: Optional[int]
    features: Optional[dict] = None
    status: Optional[str] = None
    interval: Optional[str] = None
    interval_count: Optional[int] = None
    trial_period_days: Optional[int] = None
    max_users: Optional[int] = None
    max_storage: Optional[int] = None
    max_api_calls: Optional[int] = None

class PlanUpdate(PlanBase):
    name: Optional[str] = None
    price: Optional[float] = None
    token_amount: Optional[int]

class PlanResponse(PlanBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
