from datetime import datetime, timedelta, timezone
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.configuration.settings import Configuration
from app.models.user.user import User
from app.schemas.auth.auth import AuthRequestCreate, AuthRequestUpdate
from app.auth.auth import AuthRouter
from app.database.connection import get_session
from app.middleware.admin import is_admin

db_session = get_session
configuration = Configuration()
get_current_user = AuthRouter().get_current_user

class AdminRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(prefix="/admin", *args, **kwargs)
        self.add_api_route("/users", self.list_users, methods=["GET"], response_model=List[User])
        self.add_api_route("/users", self.create_user, methods=["POST"], response_model=User)
        self.add_api_route("/recent-users", self.get_recent_users, methods=["GET"], response_model=dict)
        self.add_api_route("/users/{company_id}", self.update_user, methods=["PUT"], response_model=User)
        self.add_api_route("/users/{company_id}", self.delete_user, methods=["DELETE"], response_model=dict)

    def list_users(self, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        is_admin(current_user)
        users = session.exec(select(User)).all()
        return users

    def create_user(self, user_data: AuthRequestCreate, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        
        is_admin(current_user)
        
        # Valida duplicidade de email
        if session.exec(select(User).where(User.email == user_data.email)).first():
            raise HTTPException(status_code=409, detail="Email já está em uso por outro usuário.")

        # Valida duplicidade de username
        if session.exec(select(User).where(User.username == user_data.username)).first():
            raise HTTPException(status_code=409, detail="Username já está em uso por outro usuário.")
        
        hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
        
        db_user = User(
            name=user_data.name,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password.decode('utf-8'),
            company_id=user_data.company_id,
            is_admin=user_data.is_admin
        )
        
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        
        return db_user

    def update_user(self, company_id: int, user_data: AuthRequestUpdate, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        is_admin(current_user)
        db_user = session.get(User, company_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        # Verifica duplicidade de email (se for diferente do atual)
        if user_data.email and user_data.email != db_user.email:
            existing_email = session.exec(
                select(User).where(User.email == user_data.email, User.id != db_user.id)
            ).first()
            if existing_email:
                raise HTTPException(status_code=409, detail="Email já está em uso por outro usuário.")

        # Verifica duplicidade de username (se for diferente do atual)
        if user_data.username and user_data.username != db_user.username:
            existing_username = session.exec(
                select(User).where(User.username == user_data.username, User.id != db_user.id)
            ).first()
            if existing_username:
                raise HTTPException(status_code=409, detail="Username já está em uso por outro usuário.")

        # Atualiza senha se necessário
        if user_data.password:
            hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
            db_user.password_hash = hashed_password.decode('utf-8')

        for key, value in user_data.dict(exclude_unset=True, exclude={"password"}).items():
            setattr(db_user, key, value)

        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

    def delete_user(self, company_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        is_admin(current_user)
        db_user = session.get(User, company_id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

        session.delete(db_user)
        session.commit()
        return {"ok": True, "message": "Usuário deletado com sucesso"}

    def get_recent_users(self, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        is_admin(current_user)
        now = datetime.now(timezone.utc)
        start_of_week = now - timedelta(days=now.weekday())
        start_of_month = now.replace(day=1)

        recent_users_week = session.exec(select(User).where(User.created_at >= start_of_week)).all()
        recent_users_month = session.exec(select(User).where(User.created_at >= start_of_month)).all()

        return {
            "week": recent_users_week,
            "month": recent_users_month
        }
        

