from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.credit.credit import Credit
from app.database.connection import get_session
from app.schemas.credit.credit import CreditCreate, CreditUpdate, CreditRead

db_session = get_session

class CreditRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_api_route("/credits", self.get_credits, methods=["GET"], response_model=List[CreditRead])
        self.add_api_route("/credits", self.create_credit, methods=["POST"], response_model=CreditRead)
        self.add_api_route("/credits/{credit_id}", self.get_credit_by_id, methods=["GET"], response_model=CreditRead)
        self.add_api_route("/credits/{credit_id}", self.update_credit, methods=["PUT"], response_model=CreditRead)
        self.add_api_route("/credits/{credit_id}", self.delete_credit, methods=["DELETE"], response_model=dict)

    def get_credits(self, session: Session = Depends(db_session)):
        return session.exec(select(Credit)).all()

    def get_credit_by_id(self, credit_id: int, session: Session = Depends(db_session)):
        credit = session.get(Credit, credit_id)
        if not credit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crédito não encontrado")
        return credit

    def create_credit(self, credit_request: CreditCreate, session: Session = Depends(db_session)):
        credit = Credit(**credit_request.dict())
        session.add(credit)
        session.commit()
        session.refresh(credit)
        return credit

    def update_credit(self, credit_id: int, credit_update: CreditUpdate, session: Session = Depends(db_session)):
        credit = session.get(Credit, credit_id)
        if not credit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crédito não encontrado")

        for key, value in credit_update.dict(exclude_unset=True).items():
            setattr(credit, key, value)

        session.commit()
        session.refresh(credit)
        return credit

    def delete_credit(self, credit_id: int, session: Session = Depends(db_session)):
        credit = session.get(Credit, credit_id)
        if not credit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crédito não encontrado")

        session.delete(credit)
        session.commit()
        return {"message": "Crédito excluído com sucesso"}
