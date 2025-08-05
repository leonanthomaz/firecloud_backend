from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.finance.finance import Finance


class FinanceCategory(SQLModel, table=True):
    """Categoria para classificação de lançamentos financeiros.
    
    Atributos:
        id: Identificador único da categoria
        name: Nome da categoria
        type: Tipo (receita/despesa)
        description: Descrição detalhada
        finances: Lançamentos financeiros associados
    """
    __tablename__ = "tb_finance_category"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="ID único autoincremental da categoria",
        title="ID"
    )
    
    name: str = Field(
        ...,
        description="Nome da categoria financeira",
        max_length=50,
        title="Nome"
    )
    
    type: str = Field(
        ...,
        description="Tipo da categoria (receita/despesa)",
        title="Tipo"
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Descrição detalhada da categoria",
        title="Descrição"
    )

    # Relacionamento
    finances: list["Finance"] = Relationship(
        back_populates="category",
    )