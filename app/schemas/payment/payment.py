from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field

from app.enums.payment import PaymentMethod, PaymentType, PaymentStatus

# 🔹 Base compartilhada
class PaymentBase(BaseModel):
    type: PaymentType = Field(..., description="Tipo do item: PLAN ou CREDIT")
    reference_id: int = Field(..., description="ID do item relacionado (plano ou crédito)")
    name: Optional[str] = Field(None, description="Nome no momento da compra")
    slug: Optional[str] = Field(None, description="Slug do item no momento da compra")
    description: Optional[str] = Field(None, description="Descrição salva")

    quantity: int = Field(1, description="Quantidade do item comprado")
    amount: Decimal = Field(..., description="Valor unitário (R$)")
    total: Decimal = Field(..., description="Total pago (amount x quantity)")

    status: Optional[PaymentStatus] = Field(default=None)

    valid_from: Optional[datetime] = Field(None, description="Início da validade (se for plano)")
    valid_until: Optional[datetime] = Field(None, description="Fim da validade")
    valid_until_with_grace: Optional[datetime] = Field(None, description="Fim do período de carência")


# 🔸 Criação (POST)
class PaymentCreate(PaymentBase):
    company_id: int
    plan_id: Optional[int] = None
    credit_id: Optional[int] = None
    payment_method: Optional[str] = None

# 🔸 Atualização (PATCH)
class PaymentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    amount: Optional[Decimal] = None
    total: Optional[Decimal] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    valid_until_with_grace: Optional[datetime] = None
    status: Optional[PaymentStatus] = None
    paid_at: Optional[datetime] = None
    transaction_id: Optional[str] = None
    transaction_code: Optional[str] = None
    invoice_id: Optional[str] = None
    qr_code: Optional[str] = None
    qr_code_base64: Optional[str] = None

    class Config:
        from_attributes = True


# 🔹 Resposta completa (GET)
class PaymentResponse(PaymentBase):
    id: int
    company_id: int
    plan_id: Optional[int] = None
    credit_id: Optional[int] = None

    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    transaction_code: Optional[str] = None
    invoice_id: Optional[str] = None
    qr_code: Optional[str] = None
    qr_code_base64: Optional[str] = None
    paid_at: Optional[datetime] = None

    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        
class PaymentStatusCheck(BaseModel):
    status: PaymentStatus
    transaction_id: Optional[str] = None
    valid_until: Optional[datetime] = None
    
    class Config:
        from_attributes = True
    
class PaymentPixProcess(BaseModel):
    payment_id: int
    company_id: int
    amount: float
    
    payment_method: PaymentMethod
    
    token: Optional[str] = None  # Token do cartão, gerado no frontend
    payment_method_id: Optional[str] = None  # "visa", "master", etc.
    installments: Optional[int] = 1  # Parcelas, default 1
    document_number: Optional[str] = None  # CPF ou CNPJ do pagador
    
    qr_code: Optional[str] = None
    qr_code_base64: Optional[str] = None
 
    class Config:
            from_attributes = True