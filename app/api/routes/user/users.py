from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.auth.auth import AuthRouter
from app.database.connection import get_session
from app.models.user.user import User
from app.schemas.user.user import UserPasswordUpdate, UserResponse, UserUpdateCustomer
import bcrypt

# Inicializa a instância do DatabaseManager
db_session = get_session
get_current_user = AuthRouter().get_current_user

class UserRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(prefix="/customer", *args, **kwargs)
        self.add_api_route("/users/{user_id}", self.get_user, methods=["GET"], response_model=UserResponse)
        self.add_api_route("/users/{user_id}", self.update_user_customer, methods=["PUT"], response_model=UserResponse)
        self.add_api_route("/users/{user_id}/password", self.update_user_password, methods=["PUT"])

    def get_user(self, user_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        if current_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        return user

    def update_user_customer(self, user_id: int, user_data: UserUpdateCustomer, session: Session = Depends(db_session)):
        db_user = session.get(User, user_id)

        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

        # Verifica se o novo username já existe e não é o mesmo do próprio user
        if user_data.username and user_data.username != db_user.username:
            existing_user = session.exec(
                select(User).where(User.username == user_data.username, User.id != db_user.id)
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username já está em uso por outro usuário."
                )


        # Atualiza os campos
        db_user.first_name = user_data.first_name
        db_user.username = user_data.username
        db_user.is_admin = user_data.is_admin if user_data.is_admin else False

        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        return db_user
    
    def update_user_password(self, user_id: int, payload: UserPasswordUpdate, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        if current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")

        db_user = session.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        # Se o usuário já tem senha, precisa validar a atual
        if db_user.password_hash:
            if not payload.current_password:
                raise HTTPException(status_code=400, detail="Senha atual obrigatória")
            if not bcrypt.checkpw(payload.current_password.encode('utf-8'), db_user.password_hash.encode('utf-8')):
                raise HTTPException(status_code=400, detail="Senha atual incorreta")

        # Atualiza a senha
        new_hashed = bcrypt.hashpw(payload.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db_user.password_hash = new_hashed

        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        return {"message": "Senha atualizada com sucesso"}

