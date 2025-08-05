from datetime import datetime, time, timezone
from typing import TYPE_CHECKING, List, Optional, Dict
import uuid
from sqlmodel import Field, Relationship, SQLModel, Column, JSON

from app.enums.company import CompanyOpenEnum, CompanyStatusEnum
from app.utils.hash_utils import generate_hash

if TYPE_CHECKING:
    from app.models.company.address import Address
    from app.models.chat.assistant import Assistant
    from app.models.product.category_product import CategoryProduct
    from app.models.service.category_service import CategoryService
    from app.models.chat.chat import Chat
    from app.models.credit.credit import Credit
    from app.models.finance.finance import Finance
    from app.models.chat.interaction import Interaction
    from app.models.payment.payment import Payment
    from app.models.plan.plan import Plan
    from app.models.product.product import Product
    from app.models.service.service import Service
    from app.models.user.user import User
    from app.models.schedule.schedule import Schedule
    from app.models.schedule.schedule_slot import ScheduleSlot


class Company(SQLModel, table=True):
    """Modelo que representa uma empresa no sistema.
    
    Contém todas as informações comerciais, configurações e relacionamentos de uma empresa cadastrada.
    
    Atributos:
        id: ID único da empresa
        code: Código público de referência
        name: Nome oficial da empresa
        description: Descrição do negócio
        industry: Setor de atuação
        business_type: Tipo de negócio
        cnpj: CNPJ da empresa
        phone: Telefone para contato
        website: Site oficial
        contact_email: E-mail comercial
        social_media_links: Links de redes sociais
        logo_url: URL do logotipo
        is_open: Status de abertura
        opening_time: Horário de abertura
        closing_time: Horário de fechamento
        working_days: Dias de funcionamento
        status: Status de aprovação
        plan_id: ID do plano associado
        plan: Relacionamento com o plano
        users: Usuários associados
        products: Produtos oferecidos
        services: Serviços oferecidos
        payments: Pagamentos realizados
        categories_service: Categorias de serviço
        categories_product: Categorias de produto
        assistant: Assistente virtual
        addresses: Endereços cadastrados
        chats: Conversas associadas
        interactions: Interações com clientes
        finances: Dados financeiros
        credits: Créditos disponíveis
        schedules: Agendamentos configurados
        schedule_slots: Horários disponíveis
        is_new_company: Se uma empresa é nova
        tutorial_completed: Se o tutorial foi concluído
        feature_flags: Mapa de features
        created_at: Data de criação
        updated_at: Data de atualização
        deleted_at: Data de desativação
        updated_by: ID do usuário que atualizou
        deleted_by: ID do usuário que desativou
    """
    __tablename__ = "tb_company"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="ID único autoincremental da empresa",
        title="ID"
    )
    
    code: str = Field(
        default_factory=lambda: generate_hash(str(uuid.uuid4())),
        index=True,
        description="Código hash único para referência pública",
        title="Código"
    )

    # Informações básicas
    name: str = Field(
        ...,
        description="Nome legal da empresa",
        max_length=100,
        title="Nome"
    )
    description: Optional[str] = Field(
        default=None,
        description="Descrição detalhada das atividades da empresa",
        title="Descrição"
    )
    industry: Optional[str] = Field(
        default=None,
        description="Setor principal de atuação",
        title="Setor"
    )
    business_type: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Tipo jurídico/operacional do negócio",
        title="Tipo de Negócio"
    )

    # Documentos e contato
    cnpj: Optional[str] = Field(
        default=None,
        description="CNPJ formatado (XX.XXX.XXX/XXXX-XX)",
        title="CNPJ"
    )
    phone: Optional[str] = Field(
        default=None,
        description="Telefone para contato principal",
        title="Telefone"
    )
    website: Optional[str] = Field(
        default=None,
        description="URL do website oficial",
        title="Website"
    )
    contact_email: Optional[str] = Field(
        default=None,
        description="E-mail para contato comercial",
        title="E-mail"
    )

    # Mídia e branding
    social_media_links: Optional[Dict[str, str]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Links para redes sociais (JSON)",
        title="Redes Sociais"
    )
    logo_url: Optional[str] = Field(
        default=None,
        description="URL da imagem do logotipo",
        title="Logotipo"
    )

    # Horário comercial
    is_open: CompanyOpenEnum = Field(
        default=CompanyOpenEnum.CLOSE,
        description="Indica se a empresa está aberta no momento",
        title="Status de Abertura"
    )
    opening_time: Optional[time] = Field(
        default=None,
        description="Horário de abertura diário",
        title="Abre às"
    )
    closing_time: Optional[time] = Field(
        default=None,
        description="Horário de fechamento diário",
        title="Fecha às"
    )
    working_days: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Dias da semana que a empresa opera (em JSON)",
        title="Dias de Funcionamento"
    )

    # Status e plano
    status: CompanyStatusEnum = Field(
        default=CompanyStatusEnum.PENDING,
        description="Status de aprovação da empresa no sistema",
        title="Status"
    )
    plan_id: Optional[int] = Field(
        default=None,
        foreign_key="tb_plan.id",
        description="ID do plano de assinatura contratado",
        title="ID do Plano"
    )
    plan: Optional["Plan"] = Relationship(
        back_populates="companies",
    )

    # Relacionamentos
    users: List["User"] = Relationship(
        back_populates="company",
    )
    products: List["Product"] = Relationship(
        back_populates="company",
    )
    services: List["Service"] = Relationship(
        back_populates="company",
    )
    payments: List["Payment"] = Relationship(
        back_populates="company",
    )
    categories_service: List["CategoryService"] = Relationship(
        back_populates="company",
    )
    categories_product: List["CategoryProduct"] = Relationship(
        back_populates="company",
    )
    assistant: Optional["Assistant"] = Relationship(
        back_populates="company",
    )
    addresses: List["Address"] = Relationship(
        back_populates="company",
    )
    chats: List["Chat"] = Relationship(
        back_populates="company",
    )
    interactions: List["Interaction"] = Relationship(
        back_populates="company",
    )
    finances: List["Finance"] = Relationship(
        back_populates="company",
    )
    credits: List["Credit"] = Relationship(
        back_populates="company",
    )
    schedules: List["Schedule"] = Relationship(
        back_populates="company",
    )
    schedule_slots: List["ScheduleSlot"] = Relationship(
        back_populates="company",
    )
    
    # Onboarding e controle de features
    is_new_company: Optional[bool] = Field(
        default=True,
        description="Indica se é a primeira vez que uma empresa interage com o sistema",
        title="Empresa Nova"
    )

    tutorial_completed: Optional[bool] = Field(
        default=False,
        description="Indica se o usuário já completou o tutorial inicial",
        title="Tutorial Completo"
    )

    feature_flags: Optional[Dict[str, bool]] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Mapa de features vistas ou ativadas por esse usuário",
        title="Features Ativadas"
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
        description="Data de desativação (soft delete)",
        title="Desativado em"
    )
    updated_by: Optional[int] = Field(
        default=None,
        description="ID do usuário que fez a última atualização",
        title="Atualizado por"
    )
    deleted_by: Optional[int] = Field(
        default=None,
        description="ID do usuário que desativou o registro",
        title="Desativado por"
    )

    class Config:
        from_attributes = True