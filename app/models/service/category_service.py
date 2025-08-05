from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel


if TYPE_CHECKING:
    from app.models.company.company import Company
    from app.models.service.service import Service


class CategoryService(SQLModel, table=True):
    """Categoria de serviços associada a uma empresa.
    
    Representa um grupo de classificação para serviços oferecidos por uma empresa.
    
    Atributos:
        id: Identificador único da categoria
        nome: Nome da categoria de serviços
        company_id: Referência à empresa proprietária
        company: Relacionamento com o modelo Company
        services: Lista de serviços nesta categoria
        created_at: Data de criação do registro
        updated_at: Data da última atualização
        deleted_at: Data de desativação (soft delete)
    """
    __tablename__ = "tb_category_service"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Identificador único da categoria de serviços"
    )
    
    name: str = Field(
        ...,
        description="Nome da categoria de serviços",
        max_length=100,
        min_length=2,
        title="Nome da Categoria"
    )

    # Relacionamento com Empresa
    company_id: int = Field(
        foreign_key="tb_company.id",
        description="ID da empresa proprietária desta categoria",
        title="ID da Empresa"
    )
    company: "Company" = Relationship(
        back_populates="categories_service",
    )
    
    # Relacionamento com Serviços
    services: List["Service"] = Relationship(
        back_populates="category",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Data de criação do registro",
        title="Criado em"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Data da última atualização",
        title="Atualizado em"
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        description="Data de desativação do registro",
        title="Desativado em"
    )
    
    class Config:
        orm_mode = True