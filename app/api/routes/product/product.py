import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.configuration.settings import Configuration
from app.models.company.company import Company
from app.models.product.product import Product
from app.models.user.user import User
from app.auth.auth import AuthRouter
from app.database.connection import get_session
from app.schemas.product.product import ProductRequest

Configuration()
db_session = get_session
get_current_user = AuthRouter().get_current_user

class ProductRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/products/", self.list_products, methods=["GET"], response_model=List[Product])
        self.add_api_route("/products/", self.create_product, methods=["POST"], response_model=Product)
        self.add_api_route("/products/{product_id}", self.get_product, methods=["GET"], response_model=Product)
        self.add_api_route("/products/{product_id}", self.update_product, methods=["PUT"], response_model=Product)
        self.add_api_route("/products/{product_id}", self.delete_product, methods=["DELETE"], response_model=dict)

    def get_product(self, product_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
        return product

    def create_product(self, product_request: ProductRequest, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        logging.info(f"PRODUTOS >>> Dados recebidos: {product_request}")

        company = session.get(Company, product_request.company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empresa não encontrada")

        product = Product(
            name=product_request.name,
            description=product_request.description,
            price=product_request.price,
            category=product_request.category,
            stock=product_request.stock,
            image=product_request.image,
            code=product_request.code,
            company_id=product_request.company_id,
        )

        logging.info(f"PRODUTOS >>> Dados para salvar: {product}")

        session.add(product)
        session.commit()
        session.refresh(product)
        return product

    def list_products(self, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        products = session.query(Product).all()
        return products

    def update_product(self, product_id: int, updated_product: ProductRequest, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")

        company = session.get(Company, updated_product.company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empresa não encontrada")

        for key, value in updated_product.dict(exclude_unset=True).items():
            setattr(product, key, value)

        session.add(product)
        session.commit()
        session.refresh(product)
        return product

    def delete_product(self, product_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")

        session.delete(product)
        session.commit()
        return {"message": "Produto deletado com sucesso"}