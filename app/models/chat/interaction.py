from datetime import datetime, timezone
from typing import Optional, Dict, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel, JSON
from app.enums.chat import ChatSentiment, ChatType

if TYPE_CHECKING:
    from app.models.company.company import Company
    from app.models.chat.chat import Chat


class Interaction(SQLModel, table=True):
    """Registro de interação entre cliente e sistema.
    
    Armazena detalhes de conversas, métricas e resultados de atendimentos.
    
    Atributos:
        id: Identificador único
        company_id: ID da empresa
        company: Relacionamento com empresa
        chat_id: ID do chat associado
        chat: Relacionamento com chat
        client_name: Nome do cliente
        client_contact: Contato do cliente
        interaction_type: Tipo de interação
        channel: Canal de comunicação
        sentiment: Sentimento detectado
        interaction_summary: Resumo da interação
        outcome: Resultado obtido
        prompt_tokens: Tokens de prompt usados
        completion_tokens: Tokens de conclusão
        total_tokens: Total de tokens
        created_at: Data de criação
        updated_at: Data de atualização
        updated_by: ID do atualizador
        ai_generated_insights: Insights gerados por IA
    """
    __tablename__ = "tb_interaction"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="ID único da interação",
        title="ID"
    )

    # Relacionamentos
    company_id: int = Field(
        foreign_key="tb_company.id",
        description="ID da empresa relacionada",
        title="ID Empresa"
    )
    company: Optional["Company"] = Relationship(
        back_populates="interactions",
    )

    chat_id: int = Field(
        foreign_key="tb_chat.id",
        unique=True,
        description="ID do chat vinculado",
        title="ID Chat"
    )
    chat: Optional["Chat"] = Relationship(
        back_populates="interaction",
    )

    # Informações do cliente
    client_name: Optional[str] = Field(
        default=None,
        description="Nome do cliente (se disponível)",
        max_length=100,
        title="Nome do Cliente"
    )
    client_contact: Optional[str] = Field(
        default=None,
        description="Contato principal do cliente",
        max_length=100,
        title="Contato"
    )

    # Detalhes da interação
    interaction_type: Optional[str] = Field(
        default=None,
        description="Tipo de interação (query, support, etc)",
        title="Tipo"
    )
    channel: ChatType = Field(
        default=ChatType.CHATBOT,
        description="Canal de comunicação utilizado",
        title="Canal"
    )
    sentiment: ChatSentiment = Field(
        default=ChatSentiment.NEUTRAL,
        description="Sentimento detectado na conversa",
        title="Sentimento"
    )

    # Resultados
    interaction_summary: Optional[str] = Field(
        default=None,
        description="Resumo textual da interação",
        title="Resumo"
    )
    outcome: Optional[str] = Field(
        default=None,
        description="Resultado obtido (venda, solução, etc)",
        title="Resultado"
    )
    
    # Métricas de tokens
    prompt_tokens: Optional[int] = Field(
        default=0,
        description="Quantidade de tokens usados no prompt",
        ge=0,
        title="Tokens de Prompt"
    )
    completion_tokens: Optional[int] = Field(
        default=0,
        description="Quantidade de tokens usados na resposta",
        ge=0,
        title="Tokens de Resposta"
    )
    total_tokens: Optional[int] = Field(
        default=0,
        description="Soma total de tokens utilizados",
        ge=0,
        title="Total de Tokens"
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
    updated_by: Optional[int] = Field(
        default=None,
        description="ID do usuário que atualizou",
        title="Atualizado por"
    )

    # Análises avançadas
    ai_generated_insights: Optional[Dict] = Field(
        default=None,
        sa_type=JSON,
        description="Insights e metadados gerados por IA",
        title="Insights IA"
    )

    class Config:
        from_attributes = True