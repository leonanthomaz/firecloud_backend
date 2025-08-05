from datetime import datetime
from pydantic import BaseModel

class GoogleAuthRequest(BaseModel):
    token: str
    
class ScheduleRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    summary: str = "pending"
    description: str = None
    location: str = None
    attendees: list = None 
    reminders: dict = None 

class ScheduleUpdate(BaseModel):
    start_time: datetime
    end_time: datetime
    summary: str
    description: str = None
    location: str = None
    attendees: list = None
    reminders: dict = None