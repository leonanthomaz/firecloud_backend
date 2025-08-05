from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class ServiceBase(BaseModel):
    name: str
    description: str
    price: float
    category_id: int
    image: Optional[str] = None
    code: Optional[str] = None
    availability: Optional[bool] = True
    duration: int = 60

    class Config:
        orm_mode = True

class ServiceCreate(ServiceBase):
    company_id: int

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    image: Optional[str] = None
    code: Optional[str] = None
    availability: Optional[bool] = None
    duration: Optional[int] = None
    availability_schedule: Optional[List[dict]] = None
    updated_by: Optional[int] = None

    class Config:
        orm_mode = True

class ServiceResponse(ServiceBase):
    id: int
    company_id: int
    category_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None
    availability_schedule: List[dict] = []
    rating: float = 0.0
    reviews_count: int = 0

    class Config:
        orm_mode = True

class ServiceCard(BaseModel):
    id: int
    name: str
    price: float
    image: Optional[str] = None
    duration: int
    rating: float

    class Config:
        orm_mode = True
