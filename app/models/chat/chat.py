from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Enum as SQLEnum, Column, JSON
from typing import Optional, Dict, TYPE_CHECKING
from datetime import datetime, timezone

from app.enums.chat import ChatStep

if TYPE_CHECKING:
    from app.models.company.company import Company
    from app.models.chat.interaction import Interaction
    from app.models.chat.sentiment import Sentiment

class Chat(SQLModel, table=True):
    """Sessão de chat entre um usuário e o sistema.
    
    Rastreia estado da conversação, metadados e interações relacionadas.
    
    Atributos:
        id: Identificador único do chat
        whatsapp_id: ID da mensagem no WhatsApp
        chat_code: Código único de referência
        phone: Número de telefone do contato
        company_id: ID da empresa relacionada
        company: Relacionamento com empresa
        interaction: Interação relacionada
        human_attendance: Flag para atendimento humano
        interaction_count: Contagem atual de interações
        max_interaction: Máximo de interações permitidas
        last_interaction_at: Hora da última interação
        step: Etapa atual da conversa
        context_json: Contexto estruturado da conversa
        created_at: Criação
        updated_at: Última modificação
        deleted_at: Deleção
    """
    __tablename__ = "tb_chat"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="ID autoincremental do chat",
        title="ID do Chat"
    )
    
    # Identificadores externos
    whatsapp_id: Optional[str] = Field(
        default=None,
        index=True,
        description="ID da mensagem no WhatsApp para referência cruzada",
        max_length=255,
        title="ID do WhatsApp"
    )
    chat_code: Optional[str] = Field(
        default=None,
        index=True,
        description="Identificador único legível do chat",
        max_length=36,
        title="Código do Chat"
    )
    
    # Informações do participante
    phone: Optional[str] = Field(
        default=None,
        index=True,
        description="Número de telefone no formato E.164",
        max_length=20,
        title="Telefone"
    )

    # Relacionamentos
    company_id: int = Field(
        foreign_key="tb_company.id",
        description="Empresa proprietária desta sessão de chat",
        title="ID da Empresa"
    )
    company: Optional["Company"] = Relationship(
    )
    
    interaction: Optional["Interaction"] = Relationship(
        back_populates="chat",
    )
    
    sentiment: Optional["Sentiment"] = Relationship(
        back_populates="chat",
    )

    # Controle da conversação
    human_attendance: Optional[bool] = Field(
        default=False,
        index=True,
        description="Indica se há envolvimento de agente humano",
        title="Atendimento Humano"
    )
    
    # Rastreamento de interações
    interaction_count: Optional[int] = Field(
        default=0,
        description="Número de interações completadas",
        ge=0,
        title="Contagem de Interações"
    )
    max_interaction: Optional[int] = Field(
        default=20,
        description="Número máximo de interações permitidas antes de resetar",
        gt=0,
        title="Máximo de Interações"
    )
    last_interaction_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Data e hora da última interação",
        title="Última Interação"
    )

    # Gerenciamento de estado
    step: ChatStep = Field(
        default=ChatStep.START,
        sa_column=Column(SQLEnum(ChatStep)),
        description="Etapa atual no fluxo da conversa",
        title="Etapa do Chat"
    )
    
    # Armazenamento de contexto
    context_json: Optional[Dict] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Dados estruturados do contexto da conversa",
        title="Contexto"
    )
        
    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Data e hora de criação da sessão de chat",
        title="Criado em"
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Data e hora da última modificação",
        title="Atualizado em"
    )

    deleted_at: Optional[datetime] = Field(
        default=None,
        description="Data e hora de exclusão lógica (soft delete) da sessão",
        title="Excluído em"
    )

    class Config:
        from_attributes = True