from datetime import datetime, timedelta, timezone
import os
from typing import List
from app.enums.assistant import AssistantStatus
from app.enums.payment import PaymentType, PaymentStatus
from app.enums.register import RegisterStatusEnum
from app.models.payment.payment import Payment
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth.auth import AuthRouter
from app.configuration.settings import Configuration
from app.database.connection import get_session
from app.enums.company import CompanyStatusEnum
from app.models.chat.assistant import Assistant
from app.models.plan.plan import Plan
from app.models.company.register import Register
from app.models.company.company import Company
from app.models.user.user import User
from app.schemas.company.register import RegisterRequest, RegisterResponse, RegisterUpdate

from google.oauth2 import id_token
from google.auth.transport.requests import Request as GoogleRequest
from app.schemas.schedule.google_schedule import GoogleAuthRequest

from app.middleware.admin import is_admin
from app.utils.password_hash import hash_password 

db_session = get_session
get_current_user = AuthRouter().get_current_user
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
configuration = Configuration()


class RegisterRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/register/all", self.get_all_registers, methods=["GET"], response_model=List[RegisterResponse])
        self.add_api_route("/register/create", self.create_register, methods=["POST"], response_model=RegisterResponse)
        self.add_api_route("/register/pending", self.get_pending_registers, methods=["GET"], response_model=List[RegisterResponse])
        self.add_api_route("/register/google", self.create_register_with_google, methods=["POST"], response_model=RegisterResponse)
        self.add_api_route("/register/{id}", self.get_register, methods=["GET"], response_model=RegisterResponse)
        self.add_api_route("/register/{id}", self.complete_register, methods=["PUT"], response_model=RegisterResponse)
        self.add_api_route("/register/{id}/approve", self.approve_register, methods=["PUT"])
        self.add_api_route("/register/{id}/reject", self.reject_register, methods=["PUT"])
        
    def get_all_registers(self, session: Session = Depends(db_session), current_user: User = Depends(get_current_user)):
        is_admin(current_user)
        registers = session.exec(select(Register)).all()
        if not registers:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum registro encontrado.")
        return registers

    def get_pending_registers(self, session: Session = Depends(db_session), current_user: User = Depends(get_current_user)):
        is_admin(current_user)
        registers = session.exec(select(Register).where(Register.status == RegisterStatusEnum.PENDING)).all()
        return registers

    def get_register(self, id: int, session: Session = Depends(db_session)):
        register = session.get(Register, id)
        if not register:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado.")
        return register

    def create_register(self, register: RegisterRequest, session: Session = Depends(db_session)):
        # Verifica se email já está em uso por um usuário real
        if session.exec(select(User).where(User.email == register.email)).first():
            raise HTTPException(status_code=409, detail="Email já está em uso.")

        # Verifica se username já está em uso por um usuário real
        if session.exec(select(User).where(User.username == register.username)).first():
            raise HTTPException(status_code=409, detail="Username já está em uso.")

        # Verifica se já existe pré-cadastro pendente com mesmo email
        if session.exec(
            select(Register).where(
                (Register.email == register.email) & (Register.status == RegisterStatusEnum.PENDING)
            )
        ).first():
            raise HTTPException(status_code=409, detail="Já existe um pré-cadastro pendente com este email.")

        # Verifica se já existe pré-cadastro pendente com mesmo username
        if session.exec(
            select(Register).where(
                (Register.username == register.username) & (Register.status == RegisterStatusEnum.PENDING)
            )
        ).first():
            raise HTTPException(status_code=409, detail="Já existe um pré-cadastro pendente com este username.")

        # Hasheia a senha
        hashed_password = hash_password(register.password_hash)

        register_data = register.model_dump(exclude={"password_hash"})
        db_register = Register(**register_data, password_hash=hashed_password)

        session.add(db_register)
        session.commit()
        session.refresh(db_register)
        return db_register

    def create_register_with_google(self, request: GoogleAuthRequest, session: Session = Depends(db_session)):
        try:
            id_info = id_token.verify_oauth2_token(request.token, GoogleRequest(), GOOGLE_CLIENT_ID)
            email = id_info["email"]
            first_name = id_info.get("name", "")
            username = email.split("@")[0]

            # Verifica se email já está em uso
            if session.exec(select(User).where(User.email == email)).first():
                raise HTTPException(status_code=409, detail="Email já registrado.")

            # Verifica se username já está em uso
            if session.exec(select(User).where(User.username == username)).first():
                raise HTTPException(status_code=409, detail="Username já está em uso.")

            # Verifica se já existe pré-cadastro pendente com mesmo email
            if session.exec(
                select(Register).where(
                    (Register.email == email) & (Register.status == RegisterStatusEnum.PENDING)
                )
            ).first():
                raise HTTPException(status_code=409, detail="Já existe um pré-cadastro pendente com este email.")

            # Verifica se já existe pré-cadastro pendente com mesmo username
            if session.exec(
                select(Register).where(
                    (Register.username == username) & (Register.status == RegisterStatusEnum.PENDING)
                )
            ).first():
                raise HTTPException(status_code=409, detail="Já existe um pré-cadastro pendente com este username.")

            new_register = Register(
                first_name=first_name,
                email=email,
                username=username,
                password_hash="google",
                is_register_google=True,
                status=RegisterStatusEnum.PENDING
            )
            session.add(new_register)
            session.commit()
            session.refresh(new_register)
            return new_register

        except ValueError:
            raise HTTPException(status_code=400, detail="Token do Google inválido")
        
    def complete_register(self, id: int, data: RegisterUpdate, session: Session = Depends(db_session)):
        register = session.get(Register, id)
        if not register:
            raise HTTPException(status_code=404, detail="Registro não encontrado.")

        if register.status != RegisterStatusEnum.PENDING:
            raise HTTPException(status_code=400, detail="Cadastro já foi finalizado ou rejeitado.")

        # Atualiza os campos preenchidos
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(register, key, value)

        register.updated_at = datetime.now(timezone.utc)
        session.commit()
        session.refresh(register)

        return register
    
    def approve_register(self, id: int, session: Session = Depends(db_session), current_user: User = Depends(get_current_user)):
        is_admin(current_user)
        register = session.get(Register, id)
        if not register:
            raise HTTPException(status_code=404, detail="Registro não encontrado.")

        if register.status != RegisterStatusEnum.PENDING:
            raise HTTPException(status_code=400, detail="Registro já processado.")

        plan = session.exec(select(Plan).where(Plan.slug == register.plan_interest)).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Plano não encontrado.")

        today = datetime.now(timezone.utc)

        # 1. Cria a empresa
        company = Company(
            name=register.company_name or register.name,
            cnpj=register.cnpj,
            business_type=register.business_type,
            industry=register.industry,
            phone=register.phone,
            email=register.email,
            website=register.website,
            plan_id=plan.id,
            is_new_company=True,
            tutorial_completed=False,
            status=CompanyStatusEnum.ACTIVE
        )
        session.add(company)
        session.flush()

        # 2. Cria o usuário
        user = User(
            name=register.name,
            first_name=register.first_name,
            last_name=register.last_name,
            username=register.username,
            email=register.email,
            password_hash=register.password_hash,
            is_admin=register.is_admin,
            is_register_google=register.is_register_google,
            company_id=company.id
        )
        session.add(user)

        # 3. Define validade (assumindo plano mensal de 30 dias)
        valid_from = today
        valid_until = today + timedelta(days=30)

        # 4. Cria o pagamento
        payment_status = PaymentStatus.PAID if plan.slug == "prepaid" else PaymentStatus.PENDING
        
        valid_from = None if plan.slug == "prepaid" else datetime.now(timezone.utc)
        valid_until = None if plan.slug == "prepaid" else valid_from + timedelta(days=30)
        valid_until_with_grace = None if plan.slug == "prepaid" else valid_until + timedelta(days=5)
        
        # Cria o Payment
        payment = Payment(
            name=plan.name,
            slug=plan.slug,
            type=PaymentType.PLAN,
            reference_id=plan.id,
            amount=plan.price,
            quantity=1,
            description=plan.description,
            total=plan.price,
            valid_from=valid_from,
            valid_until=valid_until,
            valid_until_with_grace = valid_until_with_grace,
            status=payment_status,
            company_id=company.id,
            plan_id=plan.id 
        )
        session.add(payment)
        session.commit()

        # 5. Cria a assistente se necessário
        if register.assistant_preference:
            company_slug = company.name.lower().replace(" ", "-")
            if configuration.environment == "development":
                assistant_link = f"http://localhost:3000/chat/company/{company_slug}/{company.code}"
            else:
                assistant_link = f"https://firecloud.vercel.app/chat/company/{company_slug}/{company.code}"
            
            assistant = Assistant(
                company_id=company.id,
                status=AssistantStatus.OFFLINE,
                assistant_type=register.assistant_preference,
                assistant_link=assistant_link
            )
            session.add(assistant)

        # 6. Atualiza o registro
        register.status = RegisterStatusEnum.APPROVED
        register.updated_at = today

        session.commit()

        return {"message": "Cadastro aprovado com sucesso!"}

    def reject_register(self, id: int, session: Session = Depends(db_session), current_user: User = Depends(get_current_user)):
        is_admin(current_user)
        register = session.get(Register, id)
        if not register:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado.")

        register.status = RegisterStatusEnum.REJECTED
        register.updated_at = datetime.now(timezone.utc)
        session.commit()
        return {"message": "Pré-cadastro rejeitado."}
