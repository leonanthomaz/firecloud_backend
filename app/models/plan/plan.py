from datetime import datetime, timezone
from typing import List, Optional, Dict, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel, Column, JSON

if TYPE_CHECKING:
    from app.models.company.company import Company
    from app.models.payment.payment import Payment
    from app.models.credit.credit import Credit


class Plan(SQLModel, table=True):
    """Modelo que representa um plano de assinatura no sistema.
    
    Contém todas as configurações e benefícios de um plano comercial oferecido.
    
    Atributos:
        id: Identificador único
        name: Nome do plano
        description: Descrição detalhada
        price: Valor da assinatura
        token_amount: Quantidade de tokens incluídos
        features: Funcionalidades do plano
        status: Status do plano
        slug: Identificador amigável
        created_at: Data de criação
        updated_at: Data de atualização
        interval: Periodicidade de cobrança
        interval_count: Número de intervalos
        trial_period_days: Dias de teste grátis
        max_users: Máximo de usuários
        max_storage: Armazenamento máximo
        max_api_calls: Limite de chamadas API
        max_tokens: Limite total de tokens
        companies: Empresas associadas
        payments: Pagamentos vinculados
        credits: Créditos gerados
    """
    __tablename__ = "tb_plan"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="ID único do plano",
        title="ID"
    )

    # Informações básicas
    name: str = Field(
        ...,
        nullable=False,
        description="Nome comercial do plano",
        max_length=100,
        title="Nome do Plano"
    )
    description: Optional[str] = Field(
        default=None,
        description="Descrição completa dos benefícios",
        title="Descrição"
    )
    price: float = Field(
        ...,
        nullable=False,
        description="Valor mensal/anual do plano (R$)",
        gt=0,
        title="Preço"
    )

    # Configurações de tokens
    token_amount: Optional[int] = Field(
        default=None,
        description="Quantidade de tokens incluídos (se aplicável)",
        ge=0,
        title="Tokens Inclusos"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        description="Limite máximo de tokens permitidos",
        ge=0,
        title="Máximo de Tokens"
    )

    # Funcionalidades
    features: Optional[Dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Lista de funcionalidades em formato JSON",
        title="Funcionalidades"
    )

    # Status e identificação
    status: Optional[str] = Field(
        default=None,
        description="Status atual (ativo, inativo, etc)",
        title="Status"
    )
    slug: Optional[str] = Field(
        default=None,
        description="Identificador URL (ex: 'basic', 'enterprise')",
        max_length=50,
        title="Slug"
    )

    # Configurações de cobrança
    interval: Optional[str] = Field(
        default=None,
        description="Periodicidade (mensal, anual, etc)",
        title="Intervalo"
    )
    interval_count: Optional[int] = Field(
        default=None,
        description="Número de intervalos entre cobranças",
        ge=1,
        title="Contagem de Intervalos"
    )
    trial_period_days: Optional[int] = Field(
        default=None,
        description="Dias de teste gratuito",
        ge=0,
        title="Período de Teste"
    )

    # Limites do plano
    max_users: Optional[int] = Field(
        default=None,
        description="Número máximo de usuários permitidos",
        ge=1,
        title="Máximo de Usuários"
    )
    max_storage: Optional[int] = Field(
        default=None,
        description="Armazenamento incluído (em MB)",
        ge=0,
        title="Armazenamento Máximo"
    )
    max_api_calls: Optional[int] = Field(
        default=None,
        description="Limite de chamadas à API por período",
        ge=0,
        title="Máximo de Chamadas API"
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

    # Relacionamentos
    companies: List["Company"] = Relationship(
        back_populates="plan",
    )
    payments: List["Payment"] = Relationship(
        back_populates="plan",
    )
    credits: List["Credit"] = Relationship(
        back_populates="plan",
    )

    class Config:
        from_attributes = True