from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from sqlmodel import Session, func, select
from app.database.connection import get_session
from app.models.company.company import Company
from app.models.chat.interaction import Interaction

db_session = get_session

class InteractionRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/interactions/", self.create_interaction, methods=["POST"], response_model=Interaction)
        self.add_api_route("/interactions/", self.get_interactions, methods=["GET"], response_model=List[Interaction])
        self.add_api_route("/interactions/{interaction_id}", self.get_interaction, methods=["GET"], response_model=Interaction)
        self.add_api_route("/interactions/{interaction_id}", self.update_interaction, methods=["PUT"], response_model=Interaction)
        self.add_api_route("/interactions/{interaction_id}", self.delete_interaction, methods=["DELETE"], response_model=dict)
        self.add_api_route("/interactions/company/{company_id}", self.get_interactions_by_company, methods=["GET"], response_model=List[Interaction])
        # self.add_api_route("/interactions/chat/{chat_id}", self.get_interaction_by_chat, methods=["GET"], response_model=Interaction)
        self.add_api_route("/interactions/client/{client_name}", self.get_interactions_by_client_name, methods=["GET"], response_model=List[Interaction])
        self.add_api_route("/interactions/outcome/{outcome}", self.get_interactions_by_outcome, methods=["GET"], response_model=List[Interaction])
        self.add_api_route("/interactions/interest/{interest}", self.get_interactions_by_interest, methods=["GET"], response_model=List[Interaction])
        self.add_api_route("/interactions/value", self.get_interactions_by_value_range, methods=["GET"], response_model=List[Interaction])
        self.add_api_route("/interactions/date", self.get_interactions_by_date_range, methods=["GET"], response_model=List[Interaction])

    def create_interaction(self, interaction: Interaction, session: Session = Depends(db_session)):
        company = session.get(Company, interaction.company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

        db_interaction = Interaction(**interaction.dict())
        session.add(db_interaction)
        session.commit()
        session.refresh(db_interaction)
        return db_interaction

    def get_interactions(self, session: Session = Depends(db_session)):
        interactions = session.exec(select(Interaction)).all()
        return interactions

    def get_interaction(self, interaction_id: int, session: Session = Depends(db_session)):
        interaction = session.get(Interaction, interaction_id)
        if not interaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interação não encontrada")
        return interaction

    def update_interaction(self, interaction_id: int, interaction: Interaction, session: Session = Depends(db_session)):
        db_interaction = session.get(Interaction, interaction_id)
        if not db_interaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interação não encontrada")

        for key, value in interaction.dict(exclude_unset=True).items():
            setattr(db_interaction, key, value)

        session.add(db_interaction)
        session.commit()
        session.refresh(db_interaction)
        return db_interaction

    def delete_interaction(self, interaction_id: int, session: Session = Depends(db_session)):
        db_interaction = session.get(Interaction, interaction_id)
        if not db_interaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interação não encontrada")

        session.delete(db_interaction)
        session.commit()
        return {"ok": True, "message": "Interação deletada com sucesso"}

    def get_interactions_by_company(self, company_id: int, session: Session = Depends(db_session)):
        """
        Retorna todas as interações de uma empresa específica.
        """
        interactions = session.exec(select(Interaction).where(Interaction.company_id == company_id)).all()
        return interactions
    
    def get_interactions_by_client_name(self, client_name: str, session: Session = Depends(db_session)):
        interactions = session.exec(select(Interaction).where(Interaction.client_name == client_name)).all()
        return interactions

    def get_interactions_by_outcome(self, outcome: str, session: Session = Depends(db_session)):
        interactions = session.exec(select(Interaction).where(Interaction.outcome == outcome)).all()
        return interactions

    def get_interactions_by_interest(self, interest: str, session: Session = Depends(db_session)):
        interactions = session.exec(select(Interaction).where(Interaction.interest == interest)).all()
        return interactions

    def get_interactions_by_value_range(self, min: float = Query(None), max: float = Query(None), session: Session = Depends(db_session)):
        query = select(Interaction)
        if min is not None:
            query = query.where(Interaction.estimated_value >= min)
        if max is not None:
            query = query.where(Interaction.estimated_value <= max)
        interactions = session.exec(query).all()
        return interactions

    def get_interactions_by_date_range(self, start: datetime = Query(None), end: datetime = Query(None), session: Session = Depends(db_session)):
        query = select(Interaction)
        if start is not None:
            query = query.where(func.date(Interaction.created_at) >= start.date())
        if end is not None:
            query = query.where(func.date(Interaction.created_at) <= end.date())
        interactions = session.exec(query).all()
        return interactions