from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import uuid4

from sqlmodel import SQLModel, Field, Relationship

from app.enums.chat import ChatSentiment

if TYPE_CHECKING:
    from app.models.chat.chat import Chat

class Sentiment(SQLModel, table=True):
    """Registro de sentimentos agregados de um chat.

    Armazena os contadores de sentimentos detectados em uma conversa específica,
    junto com o sentimento final predominante e data de atualização.

    Atributos:
        id (str): ID único do registro de sentimento (UUID).
        chat_id (str): ID do chat relacionado.
        sentiment_positive_count (int): Quantidade de sentimentos positivos.
        sentiment_negative_count (int): Quantidade de sentimentos negativos.
        sentiment_neutral_count (int): Quantidade de sentimentos neutros.
        final_sentiment (ChatSentiment): Sentimento final predominante.
        updated_at (datetime): Data e hora da última atualização do registro.
        chat (Chat): Relacionamento com a tabela de Chat.
    """
    __tablename__ = "tb_sentiment"

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="ID único do sentimento (UUID)",
        title="ID"
    )

    chat_id: int = Field(
        foreign_key="tb_chat.id",
        unique=True,
        description="ID do chat vinculado",
        title="ID Chat"
    )

    sentiment_positive_count: int = Field(
        default=0,
        description="Quantidade de sentimentos positivos",
        title="Sentimento positivo"
    )

    sentiment_negative_count: int = Field(
        default=0,
        description="Quantidade de sentimentos negativos",
        title="Sentimento negativo"
    )

    sentiment_neutral_count: int = Field(
        default=0,
        description="Quantidade de sentimentos neutros",
        title="Sentimento neutro"
    )

    final_sentiment: Optional[ChatSentiment] = Field(
        default=None,
        description="Sentimento final predominante",
        title="Final do sentimento"
    )

    updated_at: Optional[datetime] = Field(
        default=None,
        description="Data da última atualização",
        title="Atualizado em"
    )

    chat: Optional["Chat"] = Relationship(
        back_populates="sentiment",
    )
