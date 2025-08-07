from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.company.company import Company
from app.models.chat.assistant import Assistant
from app.models.user.user import User
from app.auth.auth import AuthRouter
from app.database.connection import get_session
from app.schemas.chat.assistant import AssistantRequest, AssistantResponse, AssistantStatusUpdate, AssistantUpdate

db_session = get_session
get_current_user = AuthRouter().get_current_user

class AssistantRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/assistant/{company_id}", self.get_assistant_by_company, methods=["GET"], response_model=AssistantResponse)
        self.add_api_route("/assistants/{company_id}", self.list_assistants, methods=["GET"], response_model=List[AssistantResponse])
        self.add_api_route("/assistants/{company_id}", self.create_assistant, methods=["POST"], response_model=AssistantResponse)
        self.add_api_route("/assistants/{company_id}/{assistant_id}", self.get_assistant, methods=["GET"], response_model=AssistantResponse)
        self.add_api_route("/assistants/{company_id}/{assistant_id}", self.update_assistant, methods=["PUT"], response_model=AssistantResponse)
        self.add_api_route("/assistants/{company_id}/{assistant_id}", self.delete_assistant, methods=["DELETE"], response_model=dict)
        self.add_api_route("/assistants/{company_id}/{assistant_id}/status", self.update_assistant_status, methods=["PATCH"], response_model=AssistantResponse)


    def get_assistant_by_company(self, company_id: int, session: Session = Depends(db_session)):
        # Verificar se a empresa existe
        company = session.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

        # Verificar se a assistente pertence à empresa
        assistant = session.exec(select(Assistant).where(Assistant.company_id == company_id)).first()
        if not assistant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistente não encontrada ou não pertence à empresa")

        return assistant
    
    def get_assistant(self, company_id: int, assistant_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        # Verificar se a empresa existe
        company = session.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

        # Verificar se a assistente pertence à empresa
        assistant = session.exec(select(Assistant).where(Assistant.id == assistant_id, Assistant.company_id == company_id)).first()
        if not assistant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistente não encontrada ou não pertence à empresa")

        return assistant

    def create_assistant(self, company_id: int, assistant_request: AssistantRequest, session: Session = Depends(db_session)):
        # Verificar se a empresa existe
        company = session.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empresa não encontrada")

        # Criar a assistente
        assistant = Assistant(
            company_id=company_id,
            status=assistant_request.status,
            assistant_link=assistant_request.assistant_link,
            assistant_type=assistant_request.assistant_type,
            assistant_model=assistant_request.assistant_model,
            ai_token=assistant_request.ai_token,
            assistant_token_limit=assistant_request.assistant_token_limit,
            assistant_token_usage=assistant_request.assistant_token_usage,
            assistant_token_reset_date=assistant_request.assistant_token_reset_date,
        )

        session.add(assistant)
        session.commit()
        session.refresh(assistant)
        return assistant

    def list_assistants(self, company_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        # Verificar se a empresa existe
        company = session.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

        # Listar assistentes da empresa
        assistants = session.exec(select(Assistant).where(Assistant.company_id == company_id)).all()
        return assistants

    def update_assistant(self, company_id: int, assistant_id: int, updated_assistant: AssistantUpdate, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        # Verificar se a empresa existe
        company = session.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

        # Verificar se a assistente pertence à empresa
        assistant = session.exec(select(Assistant).where(Assistant.id == assistant_id, Assistant.company_id == company_id)).first()
        if not assistant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistente não encontrada ou não pertence à empresa")

        # Atualizar os campos da assistente
        for key, value in updated_assistant.dict(exclude_unset=True).items():
            setattr(assistant, key, value)

        session.add(assistant)
        session.commit()
        session.refresh(assistant)
        return assistant

    def delete_assistant(self, company_id: int, assistant_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(db_session)):
        # Verificar se a empresa existe
        company = session.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

        # Verificar se a assistente pertence à empresa
        assistant = session.exec(select(Assistant).where(Assistant.id == assistant_id, Assistant.company_id == company_id)).first()
        if not assistant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistente não encontrada ou não pertence à empresa")

        session.delete(assistant)
        session.commit()
        return {"message": "Assistente deletada com sucesso"}
    
    def update_assistant_status(
        self,
        company_id: int,
        assistant_id: int,
        status_update: AssistantStatusUpdate,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(db_session)
    ):
        # Verificar se a empresa existe
        company = session.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

        # Verificar se a assistente pertence à empresa
        assistant = session.exec(
            select(Assistant).where(
                Assistant.id == assistant_id,
                Assistant.company_id == company_id
            )
        ).first()

        if not assistant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistente não encontrada")

        # Atualizar status
        assistant.status = status_update.status
        assistant.updated_at = datetime.now(timezone.utc)

        session.add(assistant)
        session.commit()
        session.refresh(assistant)

        return assistant
