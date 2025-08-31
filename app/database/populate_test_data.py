# from datetime import datetime, timezone
# from sqlmodel import Session, select
# import bcrypt
# from app.models import Company, User
# from app.models.company.register import Register
# from app.enums.register import RegisterStatusEnum
# from app.models.plan.plan import Plan
# from app.utils.password_hash import hash_password

# def populate_test_data(session: Session):
#     """Popula dados de teste seguindo o fluxo completo de cadastro"""
#     # Primeiro verifica se os planos existem
#     plan_mensal = session.exec(select(Plan).where(Plan.slug == "spark")).first()
#     plan_pre_pago = session.exec(select(Plan).where(Plan.slug == "prepaid")).first()
    
#     if not plan_mensal or not plan_pre_pago:
#         print("Planos necessários não encontrados. Execute primeiro o populate_database.")
#         return
    
#     # Cria registros de pré-cadastro
#     create_test_registers(session, plan_mensal, plan_pre_pago)
    
#     # Aprova os registros (simulando a ação do admin)
#     approve_test_registers(session)

# def create_test_registers(session: Session):
#     """Cria registros de pré-cadastro para os usuários de teste"""
    
#     test_registers = [
#         {
#             "name": "Admin Geral",
#             "first_name": "Admin",
#             "last_name": "Geral",
#             "username": "admin@firecloud.com",
#             "email": "admin@firecloud.com",
#             "password_hash": hash_password("admin456"),
#             "company_name": "FireCloud Admin",
#             "cnpj": "11.111.111/0001-11",
#             "phone": "(21) 99999-9999",
#             "business_type": "service",
#             "industry": "Tecnologia",
#             "plan_interest": "spark",
#             "assistant_preference": "receptionist",
#             "is_admin": True,
#             "status": RegisterStatusEnum.PENDING
#         },
#         {
#             "name": "Empresa Mensal",
#             "first_name": "Empresa",
#             "last_name": "Mensal",
#             "username": "empresa_plano@exemplo.com",
#             "email": "empresa_plano@exemplo.com",
#             "password_hash": hash_password("empresa_plano123"),
#             "company_name": "Tech Solutions Mensal",
#             "cnpj": "22.222.222/0001-22",
#             "phone": "(21) 98888-8888",
#             "business_type": "service",
#             "industry": "Tecnologia",
#             "plan_interest": "spark",
#             "assistant_preference": "sales_assistant",
#             "is_admin": False,
#             "status": RegisterStatusEnum.PENDING
#         },
#         {
#             "name": "Empresa Pré-Pago",
#             "first_name": "Empresa",
#             "last_name": "Pré-Pago",
#             "username": "empresa_credito@exemplo.com",
#             "email": "empresa_credito@exemplo.com",
#             "password_hash": hash_password("empresa_credito123"),
#             "company_name": "Digital Services Pré-Pago",
#             "cnpj": "33.333.333/0001-33",
#             "phone": "(21) 97777-7777",
#             "business_type": "service",
#             "industry": "Tecnologia",
#             "plan_interest": "prepaid",
#             "assistant_preference": "support_assistant",
#             "is_admin": False,
#             "status": RegisterStatusEnum.PENDING
#         }
#     ]
    
#     for register_data in test_registers:
#         # Verifica se já existe um registro com esse email
#         existing_register = session.exec(
#             select(Register).where(Register.email == register_data["email"])
#         ).first()
        
#         if not existing_register:
#             register = Register(**register_data)
#             session.add(register)
    
#     session.commit()

# def approve_test_registers(session: Session):
#     """Aprova todos os registros pendentes de teste"""
#     pending_registers = session.exec(
#         select(Register).where(Register.status == RegisterStatusEnum.PENDING)
#     ).all()
    
#     for register in pending_registers:
#         # Simula a aprovação do admin
#         register.status = RegisterStatusEnum.APPROVED
#         register.updated_at = datetime.now(timezone.utc)
        
#         # Cria a empresa
#         plan = session.exec(select(Plan).where(Plan.slug == register.plan_interest)).first()
#         if not plan:
#             continue
        
#         company = Company(
#             name=register.company_name or register.name,
#             cnpj=register.cnpj,
#             business_type=register.business_type,
#             industry=register.industry,
#             phone=register.phone,
#             email=register.email,
#             website="www.exemplo.com",
#             plan_id=plan.id,
#             is_new_company=True,
#             tutorial_completed=False,
#             status="active"
#         )
#         session.add(company)
#         session.flush()  # Para obter o ID da empresa
        
#         # Cria o usuário
#         user = User(
#             name=register.name,
#             first_name=register.first_name,
#             last_name=register.last_name,
#             username=register.username,
#             email=register.email,
#             password_hash=register.password_hash,
#             is_admin=register.is_admin,
#             company_id=company.id,
#             is_active=True
#         )
#         session.add(user)
    
#     session.commit()

# def check_test_data(session: Session):
#     """Verifica se os dados de teste foram criados corretamente"""
#     print("Verificando dados de teste...")
    
#     # Verifica usuários
#     users = session.exec(select(User)).all()
#     print(f"Total de usuários: {len(users)}")
#     for user in users:
#         print(f"  - {user.name} ({user.email}) - Admin: {user.is_admin}")
    
#     # Verifica empresas
#     companies = session.exec(select(Company)).all()
#     print(f"Total de empresas: {len(companies)}")
#     for company in companies:
#         plan = session.get(Plan, company.plan_id)
#         plan_name = plan.name if plan else "Nenhum"
#         print(f"  - {company.name} - Plano: {plan_name}")
    
#     print("Verificação concluída!")

# # Para usar no seu populate principal, modifique o populate_database:
# def populate_database(session: Session):
#     """Inicializa o banco de dados e popula com dados iniciais."""
#     populate_company(session)
#     populate_admin_user(session)
#     populate_plan_pre_pago(session)
#     populate_plan_mensais(session)
#     populate_credits(session)
#     populate_test_data(session)  # Substitui populate_test_users por populate_test_data
#     check_test_data(session)  # Opcional: para verificar se tudo foi criado