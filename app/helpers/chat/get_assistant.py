# get_assistant

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.company.company import Company
from app.models.chat.assistant import Assistant
from app.auth.auth import AuthRouter
from app.database.connection import get_session

db_session = get_session
get_current_user = AuthRouter().get_current_user


def get_assistant(company_id: int, assistant_id: int, session: Session = Depends(db_session)):
        # Verificar se a empresa existe
        company = session.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

        # Verificar se a assistente pertence à empresa
        assistant = session.exec(select(Assistant).where(Assistant.id == assistant_id, Assistant.company_id == company_id)).first()
        if not assistant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistente não encontrada ou não pertence à empresa")

        return assistant