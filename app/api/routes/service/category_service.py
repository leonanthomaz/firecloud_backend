from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.service.category_service import CategoryService
from app.models.user.user import User
from app.auth.auth import AuthRouter
from app.database.connection import get_session
from app.schemas.service.category_service import CategoryRequest, CategoryUpdate

db_session = get_session
get_current_user = AuthRouter().get_current_user

class CategoryServiceRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/companies/{company_id}/categories/services", self.get_categories, methods=["GET"], response_model=List[CategoryService])
        self.add_api_route("/companies/{company_id}/categories/services", self.create_category, methods=["POST"], response_model=CategoryService)
        self.add_api_route("/companies/{company_id}/categories/services/{category_id}", self.update_category, methods=["PUT"], response_model=CategoryService)
        self.add_api_route("/companies/{company_id}/categories/services/{category_id}", self.delete_category, methods=["DELETE"], response_model=dict)

    def get_categories(self, company_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        if current_user.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário não autorizado a acessar categorias para esta empresa")

        categories = session.exec(select(CategoryService).where(CategoryService.company_id == company_id)).all()
        return categories

    def create_category(self, company_id: int, category_request: CategoryRequest, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        if current_user.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário não autorizado a criar categorias para esta empresa")

        existing_category = session.exec(select(CategoryService).where(
            CategoryService.name == category_request.name,
            CategoryService.company_id == company_id
        )).first()

        if existing_category:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Categoria com este nome já existe para esta empresa")

        category = CategoryService(name=category_request.name, company_id=company_id)
        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    def update_category(self, company_id: int, category_id: int, category_request: CategoryUpdate, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        if current_user.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário não autorizado a alterar categorias para esta empresa")

        category = session.get(CategoryService, category_id)
        if not category or category.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada ou não pertence a esta empresa")

        existing_category = session.exec(select(CategoryService).where(
            CategoryService.name == category_request.name,
            CategoryService.company_id == company_id
        )).first()

        if existing_category and existing_category.id != category_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Categoria com este nome já existe para esta empresa")

        if category_request.name:
            category.name = category_request.name

        session.commit()
        session.refresh(category)
        return category

    def delete_category(self, company_id: int, category_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        if current_user.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário não autorizado a excluir categorias para esta empresa")

        category = session.get(CategoryService, category_id)
        if not category or category.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada ou não pertence a esta empresa")

        session.delete(category)
        session.commit()
        return {"message": "Categoria excluída com sucesso"}