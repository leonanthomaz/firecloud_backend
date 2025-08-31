from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.auth.auth import AuthRouter
from app.configuration.settings import Configuration
from app.database.connection import get_session
from app.middleware.admin import is_admin
from app.models.user.user import User

session = get_session
configuration = Configuration()
get_current_user = AuthRouter().get_current_user

class LabRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/lab/populate-test-users", self.populate_users, methods=["POST"])

    def populate_users(self, current_user: User = Depends(get_current_user), session: Session = Depends(session)):
        is_admin(current_user)
        return {"status": "ok", "message": "Usuarios e empresas testes criados com sucesso!"}
