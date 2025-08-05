from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.plan.plan import Plan
from app.auth.auth import AuthRouter
from app.database.connection import get_session
from app.schemas.plan.plan import PlanRequest, PlanUpdate

db_session = get_session
get_current_user = AuthRouter().get_current_user

class PlanRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/plans", self.get_plans, methods=["GET"], response_model=List[Plan])
        self.add_api_route("/plans", self.create_plan, methods=["POST"], response_model=Plan)
        self.add_api_route("/plans/{plan_id}", self.get_plan_by_id, methods=["GET"], response_model=Plan)
        self.add_api_route("/plans/{plan_id}", self.delete_plan, methods=["DELETE"], response_model=dict)
        self.add_api_route("/plans/{plan_id}", self.update_plan, methods=["PUT"], response_model=Plan)

    def get_plans(self, session: Session = Depends(db_session)):
        plans = session.exec(select(Plan)).all()
        return plans
    
    def get_plan_by_id(self, plan_id: int, session: Session = Depends(db_session)):
        plan = session.get(Plan, plan_id)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plano não encontrado")
        return plan

    def create_plan(self, plan_request: PlanRequest, session: Session = Depends(db_session)):
        existing_plan = session.exec(select(Plan).where(Plan.name == plan_request.name)).first()
        if existing_plan:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plano com este nome já existe")

        plan = Plan(**plan_request.dict())
        session.add(plan)
        session.commit()
        session.refresh(plan)
        return plan

    def update_plan(self, plan_id: int, plan_request: PlanUpdate, session: Session = Depends(db_session)):
        plan = session.get(Plan, plan_id)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plano não encontrado")

        existing_plan = session.exec(select(Plan).where(Plan.name == plan_request.name)).first()
        if existing_plan and existing_plan.id != plan_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plano com este nome já existe")

        for key, value in plan_request.dict(exclude_unset=True).items():
            setattr(plan, key, value)

        session.commit()
        session.refresh(plan)
        return plan

    def delete_plan(self, plan_id: int, session: Session = Depends(db_session)):
        plan = session.get(Plan, plan_id)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plano não encontrado")

        session.delete(plan)
        session.commit()
        return {"message": "Plano excluído com sucesso"}
