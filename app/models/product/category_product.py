from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.company.company import Company
    from app.models.product.product import Product


class CategoryProduct(SQLModel, table=True):
    """Categoria de produtos associada a uma empresa.
    
    Attributes:
        id: Identificador único da categoria.
        name: Nome da categoria.
        company_id: ID da empresa associada.
        company: Relacionamento com a empresa.
        products: Lista de produtos nesta categoria.
        created_at: Data de criação do registro.
        updated_at: Data de última atualização.
        deleted_at: Data de desativação da categoria.
    """
    __tablename__ = "tb_category_product"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Identificador único da categoria"
    )
    
    name: str = Field(
        ...,
        description="Nome da categoria de produtos",
        max_length=100  # Adicionado sugestão de limite de caracteres
    )

    # Relacionamento com Company
    company_id: int = Field(
        foreign_key="tb_company.id",
        description="ID da empresa proprietária da categoria"
    )
    company: "Company" = Relationship(back_populates="categories_product")
    
    # Relacionamento com Product
    products: List["Product"] = Relationship(back_populates="category_product")

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Data de criação do registro"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Data da última atualização do registro"
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        description="Data de desativação da categoria"
    )

    class Config:
        orm_mode = True