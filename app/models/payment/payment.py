from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

from app.enums.payment import PaymentType, PaymentStatus

if TYPE_CHECKING:
    from app.models.company.company import Company
    from app.models.plan.plan import Plan
    from app.models.credit.credit import Credit
    from app.models.finance.finance import Finance


class Payment(SQLModel, table=True):
    """Registro de pagamento no sistema.
    
    Armazena transações financeiras relacionadas a planos ou créditos de tokens.
    
    Atributos:
        id: Identificador único
        type: Tipo do item (plano/crédito)
        reference_id: ID do item original
        name: Nome do item no momento da compra
        slug: Slug do item
        description: Descrição histórica
        payment_method: Método de pagamento
        transaction_id: ID da transação
        transaction_code: Código da transação
        invoice_id: ID da fatura
        qr_code: QR Code (se aplicável)
        qr_code_base64: QR Code em base64
        paid_at: Data de confirmação
        is_expires: Indica se expira
        quantity: Quantidade adquirida
        amount: Valor unitário
        total: Valor total
        valid_from: Data de início
        valid_until: Data de expiração
        valid_until_with_grace: Expiração com tolerância
        status: Status do pagamento
        company_id: ID da empresa
        company: Relacionamento com empresa
        plan_id: ID do plano
        plan: Relacionamento com plano
        credit_id: ID do crédito
        credit: Relacionamento com crédito
        finance_entry: Lançamento financeiro
        created_at: Data de criação
        updated_at: Data de atualização
    """
    __tablename__ = "tb_payment"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="ID único do pagamento",
        title="ID"
    )

    # Tipo e referência
    type: PaymentType = Field(
        ...,
        description="Tipo do item comprado: 'plan' (plano) ou 'credit' (crédito)",
        title="Tipo"
    )
    reference_id: int = Field(
        ...,
        description="ID original do plano ou crédito adquirido",
        title="ID Referência"
    )

    # Informações históricas
    name: Optional[str] = Field(
        default=None,
        description="Nome do plano/crédito no momento da compra",
        max_length=100,
        title="Nome"
    )
    slug: Optional[str] = Field(
        default=None,
        description="Identificador único do item no momento da compra",
        max_length=50,
        title="Slug"
    )
    description: Optional[str] = Field(
        default=None,
        description="Descrição completa no momento da compra",
        title="Descrição"
    )
    
    # Dados da transação
    payment_method: Optional[str] = Field(
        default=None,
        description="Método de pagamento utilizado",
        max_length=50,
        title="Método de Pagamento"
    )
    transaction_id: Optional[str] = Field(
        default=None,
        description="ID único da transação no gateway",
        max_length=100,
        title="ID Transação"
    )
    transaction_code: Optional[str] = Field(
        default=None,
        description="Código legível da transação",
        max_length=50,
        title="Código"
    )
    invoice_id: Optional[str] = Field(
        default=None,
        description="ID da fatura/recibo",
        max_length=100,
        title="ID Fatura"
    )
    
    # QR Code
    qr_code: Optional[str] = Field(
        default=None,
        description="URL ou conteúdo do QR Code",
        title="QR Code"
    )
    qr_code_base64: Optional[str] = Field(
        default=None,
        description="QR Code em formato base64",
        title="QR Code Base64"
    )
    
    # Status do pagamento
    paid_at: Optional[datetime] = Field(
        default=None,
        description="Data/hora de confirmação do pagamento",
        title="Pago em"
    )
    is_expires: Optional[bool] = Field(
        default=None,
        description="Indica se este pagamento tem validade",
        title="Expira?"
    )

    # Valores
    quantity: int = Field(
        default=1,
        description="Quantidade de itens adquiridos (para créditos)",
        ge=1,
        title="Quantidade"
    )
    amount: float = Field(
        ...,
        description="Valor unitário no momento da compra (R$)",
        gt=0,
        title="Valor Unitário"
    )
    total: float = Field(
        ...,
        description="Valor total pago (amount × quantity)",
        gt=0,
        title="Total"
    )

    # Validade (para planos)
    valid_from: Optional[datetime] = Field(
        default=None,
        description="Data de início da vigência",
        title="Válido de"
    )
    valid_until: Optional[datetime] = Field(
        default=None,
        description="Data de término da vigência",
        title="Válido até"
    )
    valid_until_with_grace: Optional[datetime] = Field(
        default=None,
        description="Data de expiração com período de tolerância",
        title="Válido até (com tolerância)"
    )
    
    status: PaymentStatus = Field(
        default=PaymentStatus.PENDING,
        description="Status atual do pagamento",
        title="Status"
    )
    
    # Relacionamentos
    company_id: int = Field(
        foreign_key="tb_company.id",
        description="ID da empresa que realizou o pagamento",
        title="ID Empresa"
    )
    company: Optional["Company"] = Relationship(
        back_populates="payments",
    )
    
    plan_id: int = Field(
        foreign_key="tb_plan.id",
        description="ID do plano adquirido",
        title="ID Plano"
    )
    plan: Optional["Plan"] = Relationship(
        back_populates="payments",
    )

    credit_id: Optional[int] = Field(
        default=None,
        foreign_key="tb_credit.id",
        description="ID do crédito adquirido (se aplicável)",
        title="ID Crédito"
    )
    credit: Optional["Credit"] = Relationship(
        back_populates="payments",
    )

    finance_entry: Optional["Finance"] = Relationship(
        back_populates="payment",
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
        from_attributes = True
        
    @property
    def is_expired(self) -> bool:
        """Verifica se o pagamento está expirado com base na valid_until.
        
        Returns:
            bool: True se expirado, False caso contrário
        """
        if self.valid_until:
            return datetime.now(timezone.utc) > self.valid_until
        return False