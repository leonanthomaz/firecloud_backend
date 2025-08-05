from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel


class ScheduleSlotBase(SQLModel):
    start: datetime
    end: datetime
    all_day: bool = False
    is_active: bool = True
    is_recurring: bool = False

    company_id: int
    service_id: Optional[int] = None

class ScheduleSlotCreate(ScheduleSlotBase):
    pass

class ScheduleSlotUpdate(SQLModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    all_day: Optional[bool] = None
    is_active: Optional[bool] = None
    is_recurring: Optional[bool] = None
    service_id: Optional[int] = None

class ScheduleSlotRead(ScheduleSlotBase):
    id: int
    public_id: str
    schedule_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True
