from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.product.category_product import CategoryProduct
from app.models.user.user import User
from app.auth.auth import AuthRouter
from app.database.connection import get_session
from app.schemas.product.category_product import CategoryRequest, CategoryUpdate

db_session = get_session
get_current_user = AuthRouter().get_current_user

class CategoryProductRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/companies/{company_id}/categories/products", self.get_categories, methods=["GET"], response_model=List[CategoryProduct])
        self.add_api_route("/companies/{company_id}/categories/products", self.create_category, methods=["POST"], response_model=CategoryProduct)
        self.add_api_route("/companies/{company_id}/categories/products/{category_id}", self.update_category, methods=["PUT"], response_model=CategoryProduct)
        self.add_api_route("/companies/{company_id}/categories/products/{category_id}", self.delete_category, methods=["DELETE"], response_model=dict)

    def get_categories(self, company_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        if current_user.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário não autorizado a acessar categorias de produto para esta empresa")

        categories = session.exec(select(CategoryProduct).where(CategoryProduct.company_id == company_id)).all()
        return categories

    def create_category(self, company_id: int, category_request: CategoryRequest, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        if current_user.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário não autorizado a criar categorias de produto para esta empresa")

        existing_category = session.exec(select(CategoryProduct).where(
            CategoryProduct.name == category_request.name,
            CategoryProduct.company_id == company_id
        )).first()

        if existing_category:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Categoria com este nome já existe para esta empresa")

        category = CategoryProduct(name=category_request.name, company_id=company_id)
        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    def update_category(self, company_id: int, category_id: int, category_request: CategoryUpdate, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        if current_user.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário não autorizado a alterar categorias de produto para esta empresa")

        category = session.get(CategoryProduct, category_id)
        if not category or category.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada ou não pertence a esta empresa")

        existing_category = session.exec(select(CategoryProduct).where(
            CategoryProduct.name == category_request.name,
            CategoryProduct.company_id == company_id
        )).first()

        if existing_category and existing_category.id != category_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Categoria com este nome já existe para esta empresa")

        if category_request.name:
            category.name = category_request.name
        if category_request.company_id:
            category.company_id = category_request.company_id

        session.commit()
        session.refresh(category)
        return category

    def delete_category(self, company_id: int, category_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        if current_user.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário não autorizado a excluir categorias de produto para esta empresa")

        category = session.get(CategoryProduct, category_id)
        if not category or category.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada ou não pertence a esta empresa")

        session.delete(category)
        session.commit()
        return {"message": "Categoria excluída com sucesso"}