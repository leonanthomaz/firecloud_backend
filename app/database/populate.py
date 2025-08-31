from app.enums.assistant import AssistantStatus
from app.enums.company import CompanyOpenEnum, CompanyStatusEnum
from app.models import Company, User
from app.models.chat.assistant import Assistant
from app.models.credit.credit import Credit
from app.models.plan.plan import Plan
from sqlmodel import Session, select
import bcrypt
from app.configuration.settings import Configuration
from datetime import time, timezone, datetime
import uuid
from app.models.company.address import Address
from app.utils.hash_utils import generate_hash

# Carregar configuração global
configuration = Configuration()

def populate_database(session: Session):
    """Inicializa o banco de dados e popula com dados iniciais."""
    populate_company(session)
    populate_admin_user(session)
    populate_extra_admins(session)
    populate_plan_pre_pago(session)
    populate_plan_mensais(session)
    populate_credits(session)

def get_or_create_company(session: Session, company_data: dict) -> Company:
    """Obtém uma empresa existente ou cria uma nova."""
    company = session.exec(select(Company).where(Company.name == company_data["name"])).first()
    if not company:
        company = Company(**company_data)
        session.add(company)
        session.commit()
        session.refresh(company)  # Atualiza o objeto com os dados do banco
    return company

def get_or_create_user(session: Session, user_data: dict) -> User:
    """Obtém um usuário existente ou cria um novo."""
    user = session.exec(select(User).where(User.username == user_data["username"])).first()
    if not user:
        user = User(**user_data)
        session.add(user)
        session.commit()
        session.refresh(user)  # Atualiza o objeto com os dados do banco
    return user

def generate_company_code() -> str:
    """Gera um código único para a empresa."""
    return generate_hash(str(uuid.uuid4()))

def get_assistant_link(code: str) -> str:
    """Gera o link do assistente de IA com base no ambiente."""
    if configuration.environment == "production":
        return f"https://firecloud.vercel.app/chat/company/{code}"
    else:
        return f"http://localhost:3000/chat/company/{code}"

def populate_company(session: Session):
    """Popula a tabela de empresas e assistentes, se não existirem."""
    code = generate_company_code()

    company_data = {
        "code": code,
        "name": "FireCloud",
        "description": "Empresa focada em Inteligência Artificial e Chatbots",
        "industry": "Tecnologia",
        "cnpj": "00.000.000/0001-00",
        "phone": "(21) 99809-0928",
        "address": "Rua Antonio Nunes, Alto da Boa Vista",
        "website": "firecloud-frontend.vercel.app",
        "is_new_company": True,
        
        "working_days": ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"],
        "business_type": "service",
        
        "opening_time": time(9, 0),
        "closing_time": time(18, 0),
        
        "status": CompanyStatusEnum.ACTIVE,
        "is_open": CompanyOpenEnum.OPEN,
        "created_at": datetime.now(timezone.utc),
    }

    company = get_or_create_company(session, company_data)

    # Verifica se já existe um assistente vinculado
    existing_assistant = session.exec(
        select(Assistant).where(Assistant.company_id == company.id)
    ).first()

    if not existing_assistant:
        company_slug = company.name.lower().replace(" ", "-")
        if configuration.environment == "development":
            assistant_link = f"http://localhost:3000/chat/company/{company_slug}/{company.code}"
        else:
            assistant_link = f"https://firecloud.vercel.app/chat/company/{company_slug}/{company.code}"

        assistant = Assistant(
            company_id=company.id,
            assistant_name="Tainá",
            assistant_api_url="deepseek/deepseek-prover-v2:free",
            assistant_type="receptionist", # receptionist, sales_assistant, support_assistant, booking_agent, hr_assistant
            assistant_model="GPT-3.5",
            assistant_token_limit=1000000000,
            assistant_api_key=configuration.deepseek_api_key,
            status=AssistantStatus.ONLINE,
            assistant_link=assistant_link
        )

        session.add(assistant)
        session.commit()
        session.refresh(assistant)

def populate_admin_user(session: Session):
    company = session.exec(select(Company).where(Company.name == "FireCloud")).first()
    if company:
        password_hash = hash_password("leonan2knet")
        user_data = {
            "name": "Leonan",
            "first_name": "Leonan",
            "last_name": "Oliveira",
            "email": "leonan.thomaz@gmail.com",
            "username": "leonanthomaz",
            "password_hash": password_hash,
            "company_id": company.id,
            "is_admin": True,
        }

        user = get_or_create_user(session, user_data)

        # Verifica se já existe um endereço cadastrado
        existing_address = session.exec(
            select(Address).where(Address.company_id == company.id)
        ).first()

        if not existing_address:
            address_data = Address(
                user_id=user.id,
                company_id=company.id,
                street="Rua Antonio Nunes",
                number="1",
                complement="B",
                neighborhood="Alto da Boa Vista",
                reference="Próximo ao bar do baixinho",
                city="Rio de Janeiro",
                state="RJ",
                zip_code="20531-402",
                is_company_address=True,
                is_main_address=True,
                is_home_address=False
            )
            session.add(address_data)
            session.commit()
            
def populate_extra_admins(session: Session):
    """Popula usuários admins extras, se não existirem."""
    company = session.exec(select(Company).where(Company.name == "FireCloud")).first()
    if not company:
        return

    admins = [
        {
            "name": "Leonardo",
            "first_name": "Leonardo",
            "last_name": "Oliveira",
            "username": "admin_sys",
            "email": "admin_sys@firecloud.com",
            "password": "admin_sys123",
        },
    ]

    for a in admins:
        user_data = {
            "name": a["name"],
            "first_name": a["first_name"],
            "last_name": a["last_name"],
            "username": a["username"],
            "email": a["email"],
            "password_hash": hash_password(a["password"]),
            "company_id": company.id,
            "is_admin": True,
        }
        get_or_create_user(session, user_data)

            
def populate_plan_pre_pago(session: Session):
    """Cria o plano pré-pago se não existir."""

    slug_pre_pago = "prepaid"

    existing_plan = session.exec(select(Plan).where(Plan.slug == slug_pre_pago)).first()
    if existing_plan:
        return  # já existe, não faz nada

    pre_pago = Plan(
        name="Plano Pré-Pago",
        description="Plano sem mensalidade, pagamento conforme uso. Ideal para quem quer controlar gastos.",
        price=0.0,
        features='{"chatbot": true, "suporte": false}',
        status="active",
        slug=slug_pre_pago,

        interval=None,
        interval_count=None,
        trial_period_days=None,

        max_users=1,
        max_storage=500,  # 500 MB
        max_api_calls=10000,  # 10k chamadas API
        max_tokens=1000000,  # 1 milhão tokens por mês, por ex

        created_at=datetime.now(timezone.utc)
    )
    session.add(pre_pago)
    session.commit()
    session.refresh(pre_pago)
    
def populate_credits(session: Session):
    """Cria pacotes de créditos pré-pagos para a empresa FireCloud."""

    company = session.exec(select(Company).where(Company.name == "FireCloud")).first()
    plan = session.exec(select(Plan).where(Plan.slug == "prepaid")).first()

    if not company or not plan:
        return  # Não prossegue se não tiver empresa/plano base

    credit_data = [
        {
            "name": "Pacote Ember",
            "description": "1 milhão de tokens para uso com o assistente",
            "slug": "ember-1m",
            "origin": "package",
            "features": {"expira_em_dias": 365},
            "token_amount": 1_000_000,
            "price": 29.00,
        },
        {
            "name": "Pacote Flare",
            "description": "5 milhões de tokens para uso intensivo",
            "slug": "flare-5m",
            "origin": "package",
            "features": {"expira_em_dias": 365},
            "token_amount": 3_000_000,
            "price": 49.00,
        },
        {
            "name": "Pacote WildFire",
            "description": "10 milhões de tokens para empresas que precisam de alto volume",
            "slug": "wildfire-10m",
            "origin": "package",
            "features": {"expira_em_dias": 365},
            "token_amount": 5_000_000,
            "price": 69.00,
        }
    ]

    for data in credit_data:
        existing = session.exec(
            select(Credit).where(Credit.slug == data["slug"])
        ).first()
        if not existing:
            credit = Credit(
                name=data["name"],
                description=data["description"],
                slug=data["slug"],
                origin=data["origin"],
                features=data["features"],
                token_amount=data["token_amount"],
                price=data["price"],
                company_id=company.id,
                plan_id=plan.id,
                created_at=datetime.now(timezone.utc),
            )
            session.add(credit)

    session.commit()
    
def populate_plan_mensais(session: Session):
    """Cria planos mensais Basic e Premium se ainda não existirem."""

    planos = [
        {
            "name": "Plano Basic",
            "slug": "basic",
            "price": 59.00,
            "description": "Plano básico para quem está começando com IA. Ideal para pequenos negócios.",
            "features": {
                "chatbot": True,
                "suporte": False,
                "relatorios": True
            },
            "interval": "month",
            "interval_count": 1,
            "trial_period_days": 7,
            "max_users": 2,
            "max_storage": 1000,  # 1GB
            "max_api_calls": 10000,
            "token_amount": 5_000_000,
            "max_tokens": 5_000_000,
        },
        {
            "name": "Plano Premium",
            "slug": "premium",
            "price": 99.00,
            "description": "Plano avançado com mais recursos, ideal para empresas em crescimento.",
            "features": {
                "chatbot": True,
                "suporte": True,
                "relatorios": True,
                "automacoes": True
            },
            "interval": "month",
            "interval_count": 1,
            "trial_period_days": 7,
            "max_users": 10,
            "max_storage": 5000,  # 5GB
            "max_api_calls": 100000,
            "token_amount": 10_000_000,
            "max_tokens": 10_000_000,
        }
    ]

    for plano in planos:
        existing = session.exec(select(Plan).where(Plan.slug == plano["slug"])).first()
        if not existing:
            new_plan = Plan(
                name=plano["name"],
                slug=plano["slug"],
                price=plano["price"],
                description=plano["description"],
                features=plano["features"],
                status="active",
                interval=plano["interval"],
                interval_count=plano["interval_count"],
                trial_period_days=plano["trial_period_days"],
                max_users=plano["max_users"],
                max_storage=plano["max_storage"],
                max_api_calls=plano["max_api_calls"],
                max_tokens=plano["max_tokens"],
                token_amount=plano["token_amount"],
                created_at=datetime.now(timezone.utc)
            )
            session.add(new_plan)

    session.commit()
            
def hash_password(password: str) -> str:
    """Gera um hash da senha usando bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
