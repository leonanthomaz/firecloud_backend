from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database.connection import get_session
from app.auth.auth import AuthRouter
from app.models.finance.finance import Finance
from app.schemas.finance.finance import FinanceCreate, FinanceUpdate, FinanceRead

db_session = get_session
get_current_user = AuthRouter().get_current_user

class FinanceRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/finances", self.get_finances, methods=["GET"], response_model=List[FinanceRead])
        self.add_api_route("/finances", self.create_finance, methods=["POST"], response_model=FinanceRead)
        self.add_api_route("/finances/{finance_id}", self.get_finance_by_id, methods=["GET"], response_model=FinanceRead)
        self.add_api_route("/finances/{finance_id}", self.update_finance, methods=["PUT"], response_model=FinanceRead)
        self.add_api_route("/finances/{finance_id}", self.delete_finance, methods=["DELETE"], response_model=dict)

    def get_finances(self, session: Session = Depends(db_session)):
        return session.exec(select(Finance)).all()

    def get_finance_by_id(self, finance_id: int, session: Session = Depends(db_session)):
        finance = session.get(Finance, finance_id)
        if not finance:
            raise HTTPException(status_code=404, detail="Lançamento financeiro não encontrado")
        return finance

    def create_finance(self, finance_data: FinanceCreate, session: Session = Depends(db_session)):
        finance = Finance(**finance_data.dict())
        session.add(finance)
        session.commit()
        session.refresh(finance)
        return finance

    def update_finance(self, finance_id: int, finance_data: FinanceUpdate, session: Session = Depends(db_session)):
        finance = session.get(Finance, finance_id)
        if not finance:
            raise HTTPException(status_code=404, detail="Lançamento financeiro não encontrado")

        for key, value in finance_data.dict(exclude_unset=True).items():
            setattr(finance, key, value)

        session.commit()
        session.refresh(finance)
        return finance

    def delete_finance(self, finance_id: int, session: Session = Depends(db_session)):
        finance = session.get(Finance, finance_id)
        if not finance:
            raise HTTPException(status_code=404, detail="Lançamento financeiro não encontrado")

        session.delete(finance)
        session.commit()
        return {"message": "Lançamento excluído com sucesso"}
