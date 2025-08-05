from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from app.models.company.company import Company
    from app.models.finance.finance_category import FinanceCategory
    from app.models.payment.payment import Payment


class Finance(SQLModel, table=True):
    """Registro financeiro do sistema.
    
    Representa movimentações financeiras (receitas e despesas) da empresa.
    
    Atributos:
        id: Identificador único
        amount: Valor da movimentação
        type: Tipo (receita/despesa)
        description: Descrição detalhada
        category_id: Categoria financeira
        category: Relacionamento com categoria
        related_company_id: Empresa relacionada
        company: Relacionamento com empresa
        related_payment_id: Pagamento associado
        payment: Relacionamento com pagamento
        created_at: Data de criação
        updated_at: Data de atualização
    """
    __tablename__ = "tb_finance"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="ID único do registro financeiro",
        title="ID"
    )

    # Informações financeiras
    amount: float = Field(
        ...,
        description="Valor monetário da movimentação",
        title="Valor"
    )
    
    type: str = Field(
        ...,
        description="Tipo: 'receita' ou 'despesa'",
        title="Tipo"
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Descrição detalhada da movimentação",
        max_length=255,
        title="Descrição"
    )

    # Relacionamentos
    category_id: Optional[int] = Field(
        default=None,
        foreign_key="tb_finance_category.id",
        description="ID da categoria financeira",
        title="ID Categoria"
    )
    category: Optional["FinanceCategory"] = Relationship(
        back_populates="finances",
    )

    related_company_id: Optional[int] = Field(
        default=None,
        foreign_key="tb_company.id",
        description="ID da empresa relacionada",
        title="ID Empresa"
    )
    company: Optional["Company"] = Relationship(
        back_populates="finances",
    )

    related_payment_id: Optional[int] = Field(
        default=None,
        foreign_key="tb_payment.id",
        description="ID do pagamento associado",
        title="ID Pagamento"
    )
    payment: Optional["Payment"] = Relationship(
        back_populates="finance_entry",
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

    class Config:
        orm_mode = True