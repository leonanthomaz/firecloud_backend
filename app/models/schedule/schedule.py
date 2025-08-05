from datetime import datetime, timezone
from typing import Any, Optional, TYPE_CHECKING, Dict
from sqlmodel import JSON, Column, Field, Relationship, SQLModel
from uuid import uuid4

if TYPE_CHECKING:
    from app.models.company.company import Company
    from app.models.service.service import Service
    from app.models.schedule.schedule_slot import ScheduleSlot


class Schedule(SQLModel, table=True):
    """Modelo que representa um agendamento no sistema.
    
    Compatível com FullCalendar e contém todos os dados necessários para exibição
    e gestão de agendamentos.
    
    Atributos:
        id: ID único interno
        public_id: ID público para frontend
        title: Título do evento
        start: Início do agendamento
        end: Término do agendamento
        all_day: Evento de dia inteiro
        color: Cor do evento
        company_id: ID da empresa
        company: Relacionamento com empresa
        service_id: ID do serviço
        service: Relacionamento com serviço
        status: Status do agendamento
        description: Detalhes
        location: Local do atendimento
        customer_name: Nome do cliente
        customer_contact: Contato do cliente
        slot: Relacionamento com slot
        created_at: Data de criação
        updated_at: Data de atualização
        deleted_at: Data de exclusão
        created_by: ID do criador
        extended_props: Propriedades extras
    """
    __tablename__ = "tb_schedule"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="ID único interno do agendamento",
        title="ID Interno"
    )
    
    public_id: str = Field(
        default_factory=lambda: str(uuid4()),
        unique=True,
        index=True,
        description="ID público para referência no frontend",
        title="ID Público"
    )
    
    # Campos principais para o calendário
    title: str = Field(
        ...,
        nullable=False,
        description="Título visível no calendário",
        max_length=100,
        title="Título"
    )
    start: datetime = Field(
        ...,
        nullable=False,
        description="Data e hora de início do agendamento",
        title="Início"
    )
    end: Optional[datetime] = Field(
        default=None,
        description="Data e hora de término do agendamento",
        title="Término"
    )
    all_day: bool = Field(
        default=False,
        description="Indica se é um evento de dia inteiro",
        title="Dia Inteiro?"
    )
    color: Optional[str] = Field(
        default="#3b82f6",
        description="Cor hexadecimal para exibição no calendário",
        title="Cor"
    )
    
    # Relacionamentos
    company_id: int = Field(
        foreign_key="tb_company.id",
        nullable=False,
        description="ID da empresa responsável",
        title="ID Empresa"
    )
    company: Optional["Company"] = Relationship(
        back_populates="schedules",
    )
    
    service_id: Optional[int] = Field(
        foreign_key="tb_service.id",
        description="ID do serviço agendado (se aplicável)",
        title="ID Serviço"
    )
    service: Optional["Service"] = Relationship(
        back_populates="schedules",
    )
    
    # Informações do agendamento
    status: str = Field(
        default="confirmed",
        description="Status: confirmed, pending, cancelled",
        title="Status"
    )
    description: Optional[str] = Field(
        default=None,
        description="Detalhes adicionais sobre o agendamento",
        title="Descrição"
    )
    location: Optional[str] = Field(
        default=None,
        description="Local onde ocorrerá o atendimento",
        title="Local"
    )
    customer_name: Optional[str] = Field(
        default=None,
        description="Nome completo do cliente",
        max_length=100,
        title="Cliente"
    )
    customer_contact: Optional[str] = Field(
        default=None,
        description="Telefone/email para contato",
        max_length=100,
        title="Contato"
    )
    
    slot: Optional["ScheduleSlot"] = Relationship(
        back_populates="schedule",
    )
    
    # Metadados
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
    created_by: Optional[int] = Field(
        default=None,
        description="ID do usuário que criou o agendamento",
        title="Criado por"
    )

    # Dados extras
    extended_props: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Propriedades adicionais em formato JSON",
        title="Extras"
    )

    class Config:
        from_attributes = True

    def to_calendar_event(self) -> Dict:
        """Converte o agendamento para o formato do FullCalendar.
        
        Returns:
            Dict: Dados formatados para o calendário
        """
        return {
            "id": self.public_id,
            "title": self.title,
            "start": self.start.isoformat(),
            "end": self.end.isoformat() if self.end else None,
            "color": self.color,
            "allDay": self.all_day,
            "extendedProps": {
                **self.extended_props,
                "companyId": self.company_id,
                "serviceId": self.service_id,
                "status": self.status,
                "description": self.description,
                "location": self.location,
                "customerName": self.customer_name,
                "customerContact": self.customer_contact
            }
        }