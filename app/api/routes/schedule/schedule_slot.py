from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.models.schedule.schedule_slot import ScheduleSlot
from app.schemas.schedule.schedule_slot import (
    ScheduleSlotCreate,
    ScheduleSlotRead,
    ScheduleSlotUpdate
)
from app.database.connection import get_session

db_session = get_session


class ScheduleSlotRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route(
            "/schedule-slot", self.get_slots, methods=["GET"], response_model=List[ScheduleSlotRead]
        )
        self.add_api_route(
            "/schedule-slot", self.create_slot, methods=["POST"], response_model=ScheduleSlotRead
        )
        self.add_api_route(
            "/schedule-slot/by-company", self.get_slots_by_company, methods=["GET"], response_model=List[ScheduleSlotRead]
        )
        self.add_api_route(
            "/schedule-slot/{slot_id}", self.get_slot_by_id, methods=["GET"], response_model=ScheduleSlotRead
        )
        self.add_api_route(
            "/schedule-slot/{slot_id}", self.update_slot, methods=["PUT"], response_model=ScheduleSlotRead
        )
        self.add_api_route(
            "/schedule-slot/{slot_id}", self.delete_slot, methods=["DELETE"], status_code=status.HTTP_204_NO_CONTENT
        )

    def get_slots(self, session: Session = Depends(db_session)):
        return session.exec(select(ScheduleSlot)).all()
    
    def get_slots_by_company(
        self,
        company_id: int = Query(..., description="ID da empresa"),
        session: Session = Depends(db_session)
    ):
        statement = select(ScheduleSlot).where(
            ScheduleSlot.company_id == company_id
        )
        slots = session.exec(statement).all()
        return slots

    def get_slot_by_id(self, slot_id: int, session: Session = Depends(db_session)):
        slot = session.get(ScheduleSlot, slot_id)
        if not slot:
            raise HTTPException(status_code=404, detail="Slot de agendamento não encontrado")
        return slot

    def create_slot(self, slot_data: ScheduleSlotCreate, session: Session = Depends(db_session)):
        slot = ScheduleSlot(**slot_data.dict())
        session.add(slot)
        session.commit()
        session.refresh(slot)
        return slot

    def update_slot(self, slot_id: int, slot_data: ScheduleSlotUpdate, session: Session = Depends(db_session)):
        slot = session.get(ScheduleSlot, slot_id)
        if not slot:
            raise HTTPException(status_code=404, detail="Slot de agendamento não encontrado")

        update_data = slot_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(slot, key, value)

        session.add(slot)
        session.commit()
        session.refresh(slot)
        return slot

    def delete_slot(self, slot_id: int, session: Session = Depends(db_session)):
        slot = session.get(ScheduleSlot, slot_id)
        if not slot:
            raise HTTPException(status_code=404, detail="Slot de agendamento não encontrado")
        session.delete(slot)
        session.commit()
        return None
