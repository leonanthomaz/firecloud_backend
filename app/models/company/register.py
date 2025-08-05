from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel

from app.enums.register import RegisterStatusEnum


class Register(SQLModel, table=True):
    """Registro de cadastro no sistema.
    
    Armazena informações de pré-cadastro de usuários e empresas.
    
    Atributos:
        id: Identificador único
        name: Nome completo
        first_name: Primeiro nome
        last_name: Sobrenome
        username: Nome de usuário
        password_hash: Hash da senha
        email: E-mail principal
        is_admin: Se é administrador
        is_register_google: Registrado via Google
        company_name: Nome da empresa
        cnpj: CNPJ da empresa
        business_type: Tipo de negócio
        industry: Setor de atuação
        phone: Telefone para contato
        website: Site da empresa
        plan_interest: Plano de interesse
        assistant_preference: Preferência de assistente
        privacy_policy_version: Versão dos termos
        privacy_policy_accepted_at: Data de aceite
        additional_info: Informações extras
        status: Status do registro
        created_at: Data de criação
        updated_at: Data de atualização
    """
    __tablename__ = "tb_register"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="ID único do registro",
        title="ID"
    )

    # Seção: Dados do Usuário
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
        description="Indica se é um usuário administrador",
        title="Admin?"
    )
    is_register_google: Optional[bool] = Field(
        default=None,
        description="Indica se o registro foi feito via Google",
        title="Registro Google?"
    )

    # Seção: Dados da Empresa
    company_name: Optional[str] = Field(
        default=None,
        description="Nome completo da empresa",
        max_length=100,
        title="Nome da Empresa"
    )
    cnpj: Optional[str] = Field(
        default=None,
        description="CNPJ formatado (XX.XXX.XXX/XXXX-XX)",
        max_length=18,
        title="CNPJ"
    )
    business_type: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Tipo de negócio (Restaurante, Barbearia, etc)",
        title="Tipo de Negócio"
    )
    industry: Optional[str] = Field(
        default=None,
        description="Setor de atuação principal",
        title="Setor"
    )
    phone: Optional[str] = Field(
        default=None,
        description="Telefone para contato principal",
        max_length=20,
        title="Telefone"
    )
    website: Optional[str] = Field(
        default=None,
        description="URL do website oficial",
        max_length=100,
        title="Website"
    )

    # Seção: Preferências
    plan_interest: Optional[str] = Field(
        default=None,
        description="ID do plano de interesse (pre, basic, premium)",
        title="Plano de Interesse"
    )
    assistant_preference: Optional[str] = Field(
        default=None,
        description="Tipo de assistente preferido",
        title="Assistente Preferido"
    )

    # Seção: Termos e Informações
    privacy_policy_version: Optional[str] = Field(
        default=None,
        description="Versão dos termos de política de privacidade aceitos",
        title="Versão dos Termos"
    )
    privacy_policy_accepted_at: Optional[datetime] = Field(
        default=None,
        description="Data e hora de aceite dos termos",
        title="Termos Aceitos em"
    )
    additional_info: Optional[str] = Field(
        default=None,
        description="Informações adicionais fornecidas",
        title="Informações Adicionais"
    )

    # Status
    status: RegisterStatusEnum = Field(
        default=RegisterStatusEnum.PENDING,
        description="Status atual do registro",
        title="Status"
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