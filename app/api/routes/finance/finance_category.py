from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database.connection import get_session
from app.auth.auth import AuthRouter
from app.models.finance.finance_category import FinanceCategory
from app.schemas.finance.finance_category import FinanceCategoryCreate, FinanceCategoryUpdate, FinanceCategoryRead

db_session = get_session
get_current_user = AuthRouter().get_current_user

class FinanceCategoryRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/finance-categories", self.get_categories, methods=["GET"], response_model=List[FinanceCategoryRead])
        self.add_api_route("/finance-categories", self.create_category, methods=["POST"], response_model=FinanceCategoryRead)
        self.add_api_route("/finance-categories/{category_id}", self.get_category_by_id, methods=["GET"], response_model=FinanceCategoryRead)
        self.add_api_route("/finance-categories/{category_id}", self.update_category, methods=["PUT"], response_model=FinanceCategoryRead)
        self.add_api_route("/finance-categories/{category_id}", self.delete_category, methods=["DELETE"], response_model=dict)

    def get_categories(self, session: Session = Depends(db_session)):
        return session.exec(select(FinanceCategory)).all()

    def get_category_by_id(self, category_id: int, session: Session = Depends(db_session)):
        category = session.get(FinanceCategory, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
        return category

    def create_category(self, category_data: FinanceCategoryCreate, session: Session = Depends(db_session)):
        category = FinanceCategory(**category_data.dict())
        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    def update_category(self, category_id: int, category_data: FinanceCategoryUpdate, session: Session = Depends(db_session)):
        category = session.get(FinanceCategory, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")

        for key, value in category_data.dict(exclude_unset=True).items():
            setattr(category, key, value)

        session.commit()
        session.refresh(category)
        return category

    def delete_category(self, category_id: int, session: Session = Depends(db_session)):
        category = session.get(FinanceCategory, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")

        session.delete(category)
        session.commit()
        return {"message": "Categoria excluída com sucesso"}
