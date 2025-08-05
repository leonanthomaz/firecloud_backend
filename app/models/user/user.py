from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.company.company import Company
    from app.models.company.address import Address

class User(SQLModel, table=True):
    """Modelo que representa um usuário do sistema.
    
    Atributos:
        id: Identificador único
        name: Nome completo
        first_name: Primeiro nome
        last_name: Sobrenome
        username: Nome de usuário
        password_hash: Hash da senha
        email: E-mail principal
        is_admin: Se é administrador
        company_id: ID da empresa vinculada
        company: Relacionamento com empresa
        addresses: Endereços cadastrados
        is_register_google: Registrado via Google
        token_password_reset: Token para reset de senha
        created_at: Data de criação
        updated_at: Data de atualização
        deleted_at: Data de desativação
        updated_by: ID do atualizador
        deleted_by: ID do desativador
    """
    __tablename__ = "tb_user"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="ID único do usuário",
        title="ID"
    )

    # Informações pessoais
    name: Optional[str] = Field(
        default=None,
        description="Nome completo do usuário",
        max_length=100,
        title="Nome Completo"
    )
    first_name: Optional[str] = Field(
        default=None,
        description="Primeiro nome do usuário",
        max_length=50,
        title="Primeiro Nome"
    )
    last_name: Optional[str] = Field(
        default=None,
        description="Sobrenome do usuário",
        max_length=50,
        title="Sobrenome"
    )

    # Credenciais
    username: str = Field(
        ...,
        description="Nome de usuário para login",
        max_length=50,
        title="Usuário"
    )
    password_hash: str = Field(
        ...,
        description="Hash da senha do usuário",
        title="Senha (Hash)"
    )
    email: str = Field(
        ...,
        description="E-mail principal do usuário",
        max_length=100,
        title="E-mail"
    )
    is_admin: bool = Field(
        default=False,
        description="Indica se o usuário tem privilégios de administrador",
        title="Administrador?"
    )

    # Relacionamentos
    company_id: Optional[int] = Field(
        default=None,
        foreign_key="tb_company.id",
        description="ID da empresa vinculada ao usuário",
        title="ID Empresa"
    )
    company: Optional["Company"] = Relationship(
        back_populates="users",
    )
    addresses: List["Address"] = Relationship(
        back_populates="user",
    )

    # Autenticação externa
    is_register_google: Optional[bool] = Field(
        default=None,
        description="Indica se o registro foi feito via Google",
        title="Registro Google?"
    )

    # Recuperação de senha
    token_password_reset: Optional[str] = Field(
        default=None,
        description="Token temporário para redefinição de senha",
        title="Token Reset Senha"
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
    deleted_at: Optional[datetime] = Field(
        default=None,
        description="Data de desativação do usuário",
        title="Desativado em"
    )
    updated_by: Optional[int] = Field(
        default=None,
        description="ID do usuário que fez a última atualização",
        title="Atualizado por"
    )
    deleted_by: Optional[int] = Field(
        default=None,
        description="ID do usuário que desativou a conta",
        title="Desativado por"
    )

    class Config:
        orm_mode = True