from datetime import datetime
from typing import Any, Optional, Dict
from pydantic import BaseModel, Field as PydanticField, validator
from uuid import UUID

class ScheduleBase(BaseModel):
    title: str = PydanticField(..., description="Título do agendamento")
    start: datetime = PydanticField(..., description="Data/hora de início")
    end: Optional[datetime] = PydanticField(None, description="Data/hora de término")
    all_day: bool = PydanticField(False, description="Evento de dia inteiro")
    color: Optional[str] = PydanticField("#3b82f6", description="Cor do evento (hexadecimal)")

    company_id: int = PydanticField(..., description="ID da empresa")
    service_id: Optional[int] = PydanticField(None, description="ID do serviço (opcional)")

    status: Optional[str] = PydanticField("confirmed", description="Status do agendamento")
    description: Optional[str] = PydanticField(None, description="Detalhes do agendamento")
    location: Optional[str] = PydanticField(None, description="Local do atendimento")
    customer_name: Optional[str] = PydanticField(None, description="Nome do cliente")
    customer_contact: Optional[str] = PydanticField(None, description="Contato do cliente")
    extended_props: Optional[Dict[str, Any]] = PydanticField(default_factory=dict, description="Dados extras em JSON")

    @validator("end")
    def validate_end_after_start(cls, v, values):
        if v and 'start' in values and v < values['start']:
            raise ValueError("end não pode ser antes do start")
        return v

class ScheduleCreate(ScheduleBase):
    pass  # Tudo que precisa pra criar está em ScheduleBase

class ScheduleUpdate(BaseModel):
    title: Optional[str]
    start: Optional[datetime]
    end: Optional[datetime]
    all_day: Optional[bool]
    color: Optional[str]
    company_id: Optional[int]
    service_id: Optional[int]
    status: Optional[str]
    description: Optional[str]
    location: Optional[str]
    customer_name: Optional[str]
    customer_contact: Optional[str]
    extended_props: Optional[Dict[str, Any]]

    @validator("end")
    def validate_end_after_start(cls, v, values):
        start = values.get('start')
        if v and start and v < start:
            raise ValueError("end não pode ser antes do start")
        return v

class ScheduleRead(ScheduleBase):
    id: int
    public_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    created_by: Optional[int]

    class Config:
        orm_mode = True

# Opcional: wrapper padrão de response com dados
class ScheduleResponse(BaseModel):
    data: ScheduleRead
