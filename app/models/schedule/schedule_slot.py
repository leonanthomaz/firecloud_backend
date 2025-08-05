from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from uuid import uuid4

if TYPE_CHECKING:
    from app.models.company.company import Company
    from app.models.service.service import Service
    from app.models.schedule.schedule import Schedule


class ScheduleSlot(SQLModel, table=True):
    """Modelo que representa um slot de horário disponível para agendamento.
    
    Atributos:
        id: ID único interno
        public_id: ID público para frontend
        start: Início do slot
        end: Fim do slot
        all_day: Período integral
        company_id: ID da empresa
        company: Relacionamento com empresa
        service_id: ID do serviço
        service: Relacionamento com serviço
        is_active: Status de ativação
        is_recurring: Recorrência
        schedule_id: ID do agendamento
        schedule: Relacionamento com agendamento
        created_at: Data de criação
        updated_at: Data de atualização
    """
    __tablename__ = "tb_schedule_slot"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="ID único interno do slot",
        title="ID Interno"
    )
    
    public_id: str = Field(
        default_factory=lambda: str(uuid4()),
        unique=True,
        index=True,
        description="ID público para referência no frontend",
        title="ID Público"
    )

    # Período de disponibilidade
    start: datetime = Field(
        ...,
        nullable=False,
        description="Data e hora de início da disponibilidade",
        title="Início"
    )
    end: datetime = Field(
        ...,
        nullable=False,
        description="Data e hora de término da disponibilidade",
        title="Término"
    )
    all_day: bool = Field(
        default=False,
        description="Indica disponibilidade para o dia todo",
        title="Dia Inteiro?"
    )

    # Relacionamentos
    company_id: int = Field(
        foreign_key="tb_company.id",
        nullable=False,
        description="ID da empresa dona do slot",
        title="ID Empresa"
    )
    company: Optional["Company"] = Relationship(
        back_populates="schedule_slots",
    )

    service_id: Optional[int] = Field(
        default=None,
        foreign_key="tb_service.id",
        description="ID do serviço associado (se aplicável)",
        title="ID Serviço"
    )
    service: Optional["Service"] = Relationship(
        back_populates="schedule_slots",
    )

    # Controle de status
    is_active: bool = Field(
        default=True,
        description="Indica se o slot está ativo e disponível",
        title="Ativo?"
    )
    is_recurring: bool = Field(
        default=False,
        description="Indica se é um horário recorrente (semanal, etc)",
        title="Recorrente?"
    )

    # Vinculação com agendamento
    schedule_id: Optional[int] = Field(
        default=None,
        foreign_key="tb_schedule.id",
        description="ID do agendamento que ocupou este slot",
        title="ID Agendamento"
    )
    schedule: Optional["Schedule"] = Relationship(
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Data de criação do registro",
        title="Criado em"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Data da última atualização",
        title="Atualizado em"
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        description="Data de exclusão (soft delete)",
        title="Excluído em"
    )

    class Config:
        from_attributes = True