from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

from app.enums.assistant import AssistantStatus

if TYPE_CHECKING:
    from app.models.company.company import Company


class Assistant(SQLModel, table=True):
    """Assistente virtual associado a uma empresa.
    
    Attributes:
        id: Identificador único do assistente.
        status: Status atual do assistente.
        assistant_name: Nome do assistente.
        assistant_link: URL para acessar o chat do assistente.
        assistant_type: Tipo de assistente (receptionist, sales_assistant, etc).
        assistant_model: Modelo de IA utilizado.
        assistant_api_url: Endpoint da API do assistente.
        assistant_api_key: Chave de acesso à API.
        assistant_token_limit: Limite máximo de tokens.
        assistant_token_usage: Tokens consumidos.
        assistant_token_reset_date: Data de reset do contador de tokens.
        created_at: Data de criação do registro.
        updated_at: Data de última atualização.
        company_id: ID da empresa associada.
        company: Relacionamento com a empresa.
    """
    __tablename__ = "tb_assistant"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Identificador único do assistente"
    )
    
    status: Optional[AssistantStatus] = Field(
        default=AssistantStatus.ONLINE,
        description="Status atual do assistente (online/offline)"
    )

    assistant_name: Optional[str] = Field(
        default=None,
        description="Nome de exibição do assistente"
    )
    assistant_link: Optional[str] = Field(
        default=None,
        description="URL para acessar o chat do assistente"
    )
    assistant_type: Optional[str] = Field(
        default=None,
        description="Tipo de assistente (receptionist, sales_assistant, etc)"
    )
    assistant_model: Optional[str] = Field(
        default=None,
        description="Modelo de IA utilizado pelo assistente"
    )
    assistant_api_url: Optional[str] = Field(
        default=None,
        description="Endpoint para chamadas à API do assistente"
    )
    assistant_api_key: Optional[str] = Field(
        default=None,
        description="Chave de autenticação da API",
    )
    assistant_token_limit: Optional[int] = Field(
        default=None,
        description="Limite máximo de tokens permitidos"
    )
    assistant_token_usage: Optional[int] = Field(
        default=0,
        description="Quantidade de tokens já utilizados"
    )
    assistant_token_reset_date: Optional[datetime] = Field(
        default=None,
        description="Data do próximo reset do contador de tokens"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Data de criação do registro"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Data da última atualização do registro"
    )

    # Relacionamento com a empresa
    company_id: int = Field(
        foreign_key="tb_company.id",
        description="ID da empresa proprietária do assistente"
    )
    company: "Company" = Relationship(back_populates="assistant")

    class Config:
        from_attributes = True