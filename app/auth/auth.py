import logging
from app.configuration.settings import Configuration
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlmodel import Session, select
from app.database.connection import get_session
from app.models.company.company import Company
from app.models.user.user import User
from app.schemas.company.address import AddressRead
from app.schemas.auth.auth import EmailResetRequest, PasswordResetRequest, Token
from app.schemas.auth.auth import AuthCredentials
from datetime import datetime, timedelta, timezone
import jwt
import bcrypt
import os
from google.oauth2 import id_token
from google.auth.transport.requests import Request as GoogleRequest

from app.schemas.schedule.google_schedule import GoogleAuthRequest
from app.services.email import EmailService

SECRET_KEY = os.getenv("SECRET_KEY", "UmaVezFlamengoSempreFlamengo")
JWT_EXPIRATION_HOURS = int(os.getenv("AUTH_JWT_EXPIRATION_HOURS", 1))
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

db_session = get_session
email_service = EmailService()
Configuration()

class AuthRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/login", self.login, methods=["POST"], response_model=Token)
        self.add_api_route("/auth/google", self.login_with_google, methods=["POST"], response_model=Token)
        self.add_api_route("/me", self.me, methods=["GET"])
        self.add_api_route("/validate-email", self.validate_email, methods=["POST"])
        self.add_api_route("/reset-password", self.reset_password, methods=["POST"])

    def generate_jwt(self, user_id: int) -> str:
        expiration = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
        payload = {
            "user_id": user_id,
            "exp": expiration
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token

    def decode_jwt(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    def login(self, credentials: AuthCredentials, session: Session = Depends(db_session)):
        user = session.exec(select(User).where(User.username == credentials.username)).first()
        if user and bcrypt.checkpw(credentials.password.encode('utf-8'), user.password_hash.encode('utf-8')):
            token = self.generate_jwt(user.id)
            return Token(token=token)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
        
    def get_current_user(self, authorization: str = Header(None), session: Session = Depends(db_session)) -> User:
        if not authorization:
            raise HTTPException(status_code=401, detail="Acesso não autorizado")

        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="Formato de autenticação inválido")

        token = parts[1]
        payload = self.decode_jwt(token)
        user = session.get(User, payload["user_id"])

        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return user

    def me(self, authorization: str = Header(None), session: Session = Depends(db_session)):
        user = self.get_current_user(authorization, session)
        if user is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        company = session.get(Company, user.company_id)
        if company is None:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")

        company_data = {
            "id": company.id,
            "code": company.code,
            "name": company.name,
            "description": company.description,
            "industry": company.industry,
            "business_type": company.business_type,
            "cnpj": company.cnpj,
            "phone": company.phone,
            "website": company.website,
            "contact_email": company.contact_email,
            "social_media_links": company.social_media_links,
            "logo_url": company.logo_url,
            "is_open": company.is_open,
            "opening_time": company.opening_time,
            "closing_time": company.closing_time,
            "working_days": company.working_days,
            "status": company.status,
            "plan_id": company.plan_id,
            "addresses": [AddressRead.model_validate(a).model_dump() for a in company.addresses],
            "is_new_company": company.is_new_company,
            "tutorial_completed": company.tutorial_completed,
            "feature_flags": company.feature_flags,
            "created_at": company.created_at,
            "updated_at": company.updated_at,
            "deleted_at": company.deleted_at,
            "updated_by": company.updated_by,
            "deleted_by": company.deleted_by,
        }

        return {
            "user": {
                "id": user.id,
                "name": user.name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "username": user.username,
                "is_admin": user.is_admin,
                "is_register_google": user.is_register_google,
            },
            "company": company_data,
        }

    def login_with_google(self, request: GoogleAuthRequest, session: Session = Depends(db_session)):
        logging.info(f"Dados da requisição do google: {request}")
        try:
            # Valida o token do Google
            id_info = id_token.verify_oauth2_token(request.token, GoogleRequest(), GOOGLE_CLIENT_ID)
            email = id_info['email']

            # Verifica se o usuário já existe
            user = session.exec(select(User).where(User.email == email)).first()
            
            # Gera token JWT
            token = self.generate_jwt(user.id)
            return Token(token=token)
        except ValueError:
            raise HTTPException(status_code=400, detail="Token do Google inválido")

    def validate_email(self, data: EmailResetRequest, session: Session = Depends(db_session)):
        user = session.exec(select(User).where(User.email == data.email)).first()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        
        # Gera um token de validação de email
        token = self.generate_jwt(user.id)
        
        user.token_password_reset = token
        session.commit()
        
        # Cria a URL completa para o link de redefinição de senha
        reset_link = f"http://firecloud-frontend.vercel.app/change-password/{token}"
        # reset_link = f"http://localhost:3000/change-password/{token}"

        # Envia o link de redefinição de senha por e-mail
        email_service.send_validate_email(email=user.email, link=reset_link, background_tasks=None)
        
        return {"message": "Link de validação enviado para o email", "token": token}
    
    def reset_password(self, password_request: PasswordResetRequest, session: Session = Depends(db_session)):
        # Verifica se o token de redefinição de senha é válido
        payload = self.decode_jwt(password_request.token)
        user_id = payload["user_id"]
        
        # Verifica se o usuário existe
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

        token_expiration = self.get_token_expiration(payload)
        
        if token_expiration < datetime.now(tz=timezone.utc):
            # Se expirou, apaga o token e força o usuário a refazer o processo de validação de email
            user.token_password_reset = None
            session.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O token de redefinição de senha expirou. Por favor, solicite um novo.")
        
        # Atualiza a senha do usuário
        hashed_password = bcrypt.hashpw(password_request.password.encode('utf-8'), bcrypt.gensalt())
        user.password_hash = hashed_password.decode('utf-8')
        user.token_password_reset = None
        session.commit()
        
        return {"message": "Senha redefinida com sucesso"}
    
    def get_token_expiration(self, payload: dict) -> datetime:
        # Aqui você pode usar o payload do JWT para extrair a data de expiração
        # Exemplo: Se o token tem um campo 'exp' que indica a expiração em segundos
        expiration_timestamp = payload.get("exp")
        if expiration_timestamp:
            # Cria um datetime com timezone UTC
            return datetime.fromtimestamp(expiration_timestamp, tz=timezone.utc)
        return datetime.now(tz=timezone.utc) 