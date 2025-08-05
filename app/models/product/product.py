from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.company.company import Company
    from app.models.product.category_product import CategoryProduct


class Product(SQLModel, table=True):
    """Modelo que representa um produto no sistema.
    
    Contém todas as informações sobre produtos oferecidos pelas empresas.
    
    Atributos:
        id: Identificador único
        name: Nome do produto
        description: Descrição detalhada
        price: Preço de venda
        category: Categoria principal
        stock: Quantidade em estoque
        image: URL da imagem
        company_id: ID da empresa
        company: Relacionamento com empresa
        category_id: ID da categoria
        category_product: Relacionamento com categoria
        code: Código interno
        sku: Código SKU
        tags: Tags de classificação
        rating: Avaliação média
        reviews_count: Número de avaliações
        weight: Peso do produto
        dimensions: Dimensões físicas
        material: Material principal
        color: Cor predominante
        manufacturer: Fabricante
        warranty: Garantia oferecida
        created_at: Data de criação
        updated_at: Data de atualização
        deleted_at: Data de desativação
        updated_by: ID do atualizador
        deleted_by: ID do desativador
    """
    __tablename__ = "tb_product"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="ID único do produto",
        title="ID"
    )

    # Informações básicas
    name: str = Field(
        ...,
        nullable=False,
        description="Nome comercial do produto",
        max_length=100,
        title="Nome"
    )
    description: Optional[str] = Field(
        default=None,
        description="Descrição detalhada do produto",
        title="Descrição"
    )
    price: float = Field(
        ...,
        nullable=False,
        description="Preço de venda (R$)",
        gt=0,
        title="Preço"
    )
    
    # Estoque e imagem
    stock: Optional[int] = Field(
        default=None,
        description="Quantidade disponível em estoque",
        ge=0,
        title="Estoque"
    )
    image: Optional[str] = Field(
        default=None,
        description="URL da imagem principal do produto",
        title="Imagem"
    )

    # Relacionamentos
    company_id: int = Field(
        foreign_key="tb_company.id",
        description="ID da empresa que oferece o produto",
        title="ID Empresa"
    )
    company: Optional["Company"] = Relationship(
        back_populates="products",
    )
    
    category_id: int = Field(
        foreign_key="tb_category_product.id",
        description="ID da categoria principal",
        title="ID Categoria"
    )
    category_product: Optional["CategoryProduct"] = Relationship(
        back_populates="products",
    )

    # Identificação
    code: Optional[str] = Field(
        default=None,
        description="Código interno do produto",
        max_length=50,
        title="Código"
    )
    sku: Optional[str] = Field(
        default=None,
        description="Código SKU (Stock Keeping Unit)",
        max_length=50,
        title="SKU"
    )
    
    # Classificação
    tags: str = Field(
        default="[]",
        description="Tags de classificação em formato JSON",
        title="Tags"
    )
    rating: Optional[float] = Field(
        default=None,
        description="Avaliação média (0-5)",
        ge=0,
        le=5,
        title="Avaliação"
    )
    reviews_count: Optional[int] = Field(
        default=0,
        description="Número total de avaliações",
        ge=0,
        title="Nº de Avaliações"
    )

    # Especificações técnicas
    weight: Optional[float] = Field(
        default=None,
        description="Peso em gramas",
        gt=0,
        title="Peso (g)"
    )
    dimensions: Optional[str] = Field(
        default=None,
        description="Dimensões (altura x largura x profundidade)",
        title="Dimensões"
    )
    material: Optional[str] = Field(
        default=None,
        description="Material principal de fabricação",
        title="Material"
    )
    color: Optional[str] = Field(
        default=None,
        description="Cor predominante",
        title="Cor"
    )

    # Informações do fabricante
    manufacturer: Optional[str] = Field(
        default=None,
        description="Nome do fabricante",
        title="Fabricante"
    )
    warranty: Optional[str] = Field(
        default=None,
        description="Termos da garantia",
        title="Garantia"
    )

    # Timestamps e auditoria
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
        description="Data de desativação do produto",
        title="Desativado em"
    )
    updated_by: Optional[int] = Field(
        default=None,
        description="ID do usuário que atualizou",
        title="Atualizado por"
    )
    deleted_by: Optional[int] = Field(
        default=None,
        description="ID do usuário que desativou",
        title="Desativado por"
    )

    class Config:
        from_attributes = True