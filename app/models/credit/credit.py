from datetime import datetime, timezone
from typing import Optional, Dict, TYPE_CHECKING, List
from sqlmodel import SQLModel, Field, Relationship, Column, JSON

if TYPE_CHECKING:
    from app.models.company.company import Company
    from app.models.plan.plan import Plan
    from app.models.payment.payment import Payment


class Credit(SQLModel, table=True):
    """Modelo que representa créditos de tokens no sistema.
    
    Registra pacotes de tokens adquiridos por empresas, seja via plano, pacotes avulsos ou bônus.
    
    Atributos:
        id: Identificador único
        name: Nome do pacote
        description: Descrição detalhada
        slug: Identificador amigável
        origin: Origem dos créditos
        features: Funcionalidades extras
        token_amount: Quantidade de tokens
        price: Valor pago
        company_id: Empresa beneficiada
        company: Relacionamento com empresa
        plan_id: Plano associado
        plan: Relacionamento com plano
        payments: Pagamentos vinculados
        created_at: Data de criação
    """
    __tablename__ = "tb_credit"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="ID único autoincremental",
        title="ID"
    )

    # Informações descritivas
    name: Optional[str] = Field(
        default=None,
        description="Nome comercial do pacote (ex: 'Pacote 1M tokens')",
        max_length=100,
        title="Nome do Crédito"
    )
    description: Optional[str] = Field(
        default=None,
        description="Descrição detalhada das condições do pacote",
        title="Descrição"
    )
    slug: Optional[str] = Field(
        default=None,
        description="Identificador URL amigável (ex: 'pre-pago-1m')",
        max_length=50,
        title="Slug"
    )
    origin: str = Field(
        ...,
        description="Tipo de origem: 'plano', 'pacote', 'bônus', 'promocional'",
        title="Origem"
    )

    # Configurações e benefícios
    features: Optional[Dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Funcionalidades extras em formato JSON",
        title="Features"
    )

    # Valores monetários
    token_amount: int = Field(
        ...,
        description="Quantidade total de tokens incluídos",
        ge=0,
        title="Quantidade de Tokens"
    )
    price: float = Field(
        default=0.0,
        description="Valor monetário pago (em R$)",
        ge=0.0,
        title="Preço"
    )

    # Relacionamentos
    company_id: int = Field(
        foreign_key="tb_company.id",
        description="ID da empresa beneficiária",
        title="ID da Empresa"
    )
    company: Optional["Company"] = Relationship(
        back_populates="credits",
    )

    plan_id: Optional[int] = Field(
        default=None,
        foreign_key="tb_plan.id",
        description="ID do plano associado (se aplicável)",
        title="ID do Plano"
    )
    plan: Optional["Plan"] = Relationship(
        back_populates="credits",
    )

    payments: List["Payment"] = Relationship(
        back_populates="credit",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Data de criação do registro",
        title="Criado em"
    )

    class Config:
        from_attributes = True