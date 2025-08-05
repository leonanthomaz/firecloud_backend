from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user.user import User
    from app.models.company.company import Company


class Address(SQLModel, table=True):
    """Endereço associado a usuários ou empresas.
    
    Attributes:
        id: Identificador único do endereço.
        street: Nome da rua/avenida.
        number: Número do endereço.
        complement: Complemento do endereço.
        neighborhood: Bairro.
        zip_code: CEP no formato XXXXX-XXX.
        city: Cidade (opcional).
        state: Estado (opcional).
        reference: Ponto de referência (opcional).
        is_company_address: Indica se é endereço de empresa.
        is_home_address: Indica se é endereço residencial.
        is_main_address: Indica se é o endereço principal.
        user_id: ID do usuário associado (opcional).
        user: Relacionamento com o usuário.
        company_id: ID da empresa associada (opcional).
        company: Relacionamento com a empresa.
        created_at: Data de criação do registro.
        updated_at: Data de atualização do registro (opcional).
        deleted_at: Data de desativação do registro (opcional).
    """
    __tablename__ = "tb_address"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Identificador único do endereço"
    )

    street: str = Field(..., description="Nome da rua/avenida")
    number: str = Field(..., description="Número do endereço")
    complement: str = Field(..., description="Complemento do endereço")
    neighborhood: str = Field(..., description="Bairro")
    zip_code: str = Field(..., description="CEP no formato XXXXX-XXX")

    city: Optional[str] = Field(
        default=None,
        description="Cidade"
    )
    state: Optional[str] = Field(
        default=None,
        description="Estado"
    )
    reference: Optional[str] = Field(
        default=None,
        description="Ponto de referência"
    )

    is_company_address: bool = Field(
        default=False,
        description="Indica se é endereço de empresa"
    )
    is_home_address: Optional[bool] = Field(
        default=False,
        description="Indica se é endereço residencial"
    )
    is_main_address: bool = Field(
        default=False,
        description="Indica se é o endereço principal"
    )

    user_id: Optional[int] = Field(
        default=None,
        foreign_key="tb_user.id",
        description="ID do usuário associado"
    )
    user: Optional["User"] = Relationship(back_populates="addresses")

    company_id: Optional[int] = Field(
        default=None,
        foreign_key="tb_company.id",
        description="ID da empresa associada"
    )
    company: Optional["Company"] = Relationship(back_populates="addresses")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Data de criação do registro"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Data de atualização do registro"
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        description="Data de desativação do registro"
    )

    class Config:
        orm_mode = True