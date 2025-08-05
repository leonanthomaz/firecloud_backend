from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.models.schedule.schedule import Schedule
from app.schemas.schedule.schedule import ScheduleCreate, ScheduleRead, ScheduleUpdate
from app.database.connection import get_session

db_session = get_session

class ScheduleRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/schedule", self.get_schedules, methods=["GET"], response_model=List[ScheduleRead])
        self.add_api_route("/schedule", self.create_schedule, methods=["POST"], response_model=ScheduleRead)
        self.add_api_route("/schedule/by-company", self.get_schedule_by_company, methods=["GET"], response_model=List[ScheduleRead])
        self.add_api_route("/schedule/{schedule_id}", self.get_schedule_by_id, methods=["GET"], response_model=ScheduleRead)
        self.add_api_route("/schedule/{schedule_id}", self.update_schedule, methods=["PUT"], response_model=ScheduleRead)
        self.add_api_route("/schedule/{schedule_id}", self.delete_schedule, methods=["DELETE"], response_model=None, status_code=status.HTTP_204_NO_CONTENT)

    def get_schedules(self, session: Session = Depends(db_session)):
        schedules = session.exec(select(Schedule)).all()
        return schedules

    def get_schedule_by_id(self, schedule_id: int, session: Session = Depends(db_session)):
        schedule = session.get(Schedule, schedule_id)
        if not schedule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")
        return schedule
    
    def get_schedule_by_company(
        self,
        company_id: int = Query(..., description="ID da empresa"),
        session: Session = Depends(db_session)
    ):
        statement = select(Schedule).where(
            Schedule.company_id == company_id
        )
        schedules = session.exec(statement)
        return schedules


    def create_schedule(self, schedule_request: ScheduleCreate, session: Session = Depends(db_session)):
        schedule = Schedule(**schedule_request.dict())
        session.add(schedule)
        session.commit()
        session.refresh(schedule)
        return schedule

    def update_schedule(self, schedule_id: int, schedule_request: ScheduleUpdate, session: Session = Depends(db_session)):
        schedule = session.get(Schedule, schedule_id)
        if not schedule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")
        
        update_data = schedule_request.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(schedule, key, value)
        
        session.add(schedule)
        session.commit()
        session.refresh(schedule)
        return schedule

    def delete_schedule(self, schedule_id: int, session: Session = Depends(db_session)):
        schedule = session.get(Schedule, schedule_id)
        if not schedule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")
        session.delete(schedule)
        session.commit()
        return None
