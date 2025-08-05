from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from uuid import uuid4
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.company.company import Company
    from app.models.service.category_service import CategoryService
    from app.models.schedule.schedule import Schedule
    from app.models.schedule.schedule_slot import ScheduleSlot


class Service(SQLModel, table=True):
    """Modelo que representa um serviço oferecido por uma empresa.
    
    Atributos:
        id: Identificador único
        name: Nome do serviço
        description: Descrição detalhada
        price: Preço do serviço
        code: Código identificador
        image: URL da imagem
        company_id: ID da empresa
        company: Relacionamento com empresa
        category_id: ID da categoria
        category: Relacionamento com categoria
        schedules: Agendamentos disponíveis
        schedule_slots: Horários agendados
        availability: Disponibilidade
        duration: Duração em minutos
        rating: Avaliação média
        reviews_count: Número de avaliações
        created_at: Data de criação
        updated_at: Data de atualização
        deleted_at: Data de desativação
        updated_by: ID do atualizador
        deleted_by: ID do desativador
    """
    __tablename__ = "tb_service"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="ID único do serviço",
        title="ID"
    )

    # Informações básicas
    name: str = Field(
        ...,
        nullable=False,
        description="Nome comercial do serviço",
        max_length=100,
        title="Nome"
    )
    description: str = Field(
        ...,
        nullable=False,
        description="Descrição completa do serviço",
        title="Descrição"
    )
    price: float = Field(
        ...,
        nullable=False,
        description="Preço do serviço (R$)",
        gt=0,
        title="Preço"
    )

    # Identificação
    code: str = Field(
        default_factory=lambda: uuid4().hex[:8],
        nullable=False,
        description="Código único de identificação",
        title="Código"
    )
    image: Optional[str] = Field(
        default=None,
        description="URL da imagem ilustrativa",
        title="Imagem"
    )

    # Relacionamentos
    company_id: int = Field(
        foreign_key="tb_company.id",
        description="ID da empresa que oferece o serviço",
        title="ID Empresa"
    )
    company: Optional["Company"] = Relationship(
        back_populates="services",
    )
    
    category_id: int = Field(
        foreign_key="tb_category_service.id",
        description="ID da categoria principal",
        title="ID Categoria"
    )
    category: Optional["CategoryService"] = Relationship(
        back_populates="services",
    )
    
    schedules: List["Schedule"] = Relationship(
        back_populates="service",
    )
    schedule_slots: List["ScheduleSlot"] = Relationship(
        back_populates="service",
    )

    # Disponibilidade
    availability: bool = Field(
        default=True,
        description="Indica se o serviço está disponível",
        title="Disponível?"
    )
    duration: int = Field(
        default=60,
        description="Duração estimada em minutos",
        gt=0,
        title="Duração (min)"
    )

    # Avaliações
    rating: float = Field(
        default=0.0,
        description="Avaliação média (0-5)",
        ge=0,
        le=5,
        title="Avaliação"
    )
    reviews_count: int = Field(
        default=0,
        description="Número total de avaliações",
        ge=0,
        title="Nº de Avaliações"
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
        description="Data de desativação do serviço",
        title="Desativado em"
    )

    # Auditoria
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