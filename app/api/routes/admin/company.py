from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth.auth import AuthRouter
from app.configuration.settings import Configuration
from app.middleware.admin import is_admin
from app.models.company.address import Address
from app.models.company.company import Company
from app.models.user.user import User
from app.schemas.company.company import CompanyRequest
from app.database.connection import get_session
from app.services.email import EmailService
from app.utils.hash_utils import generate_hash

# Inicializa a instância do DatabaseManager
db_session = get_session
email_service = EmailService()
configuration = Configuration()
get_current_user = AuthRouter().get_current_user

class CompanyRouter(APIRouter):
    """
    Roteador para operações relacionadas a empresas.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(prefix="/admin/company", *args, **kwargs)

        self.add_api_route("/all", self.get_all_companies, methods=["GET"], response_model=List[Company])
        self.add_api_route("/create", self.create_company, methods=["POST"], response_model=Company)
        self.add_api_route("/{company_id}", self.delete_company, methods=["DELETE"], response_model=dict)


    def get_all_companies(self, session: Session = Depends(db_session)):
        companies = session.exec(select(Company)).all()
        if not companies:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma empresa encontrada.")
        return companies

    def create_company(self, data: CompanyRequest, session: Session = Depends(db_session), current_user: User = Depends(get_current_user)):
        is_admin(current_user)
        existing_company = session.exec(select(Company).where(Company.name == data.name)).first()

        if existing_company:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empresa já existente.")

        db_company = Company(
            name=data.name,
            description=data.description,
            industry=data.industry,
            addresses=[Address(**addr.model_dump()) for addr in data.addresses],
            cnpj=data.cnpj,
            phone=data.phone,
            website=data.website,
            opening_time=data.opening_time,
            closing_time=data.closing_time,
            working_days=data.working_days,
            assistant_type=data.assistant_type,
            assistant_model=data.assistant_model,
            ai_token=data.ai_token,
            status=data.status,
            social_media_links=data.social_media_links,
            contact_email=data.contact_email,
            business_type= data.business_type
        )
                
        if not db_company.code:
            db_company.code = generate_hash(str(uuid.uuid4()))

        base_url = configuration.base_url + "/chat/company/"

        try:
            session.add(db_company)
            session.commit()
            session.refresh(db_company)
            
            db_company.assistant_link = base_url + db_company.code
            session.commit()
            
            
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        return db_company

    def delete_company(self, company_id: int, session: Session = Depends(db_session), current_user: User = Depends(get_current_user)):
        """
        Deleta uma empresa existente.
        """
        is_admin(current_user)
        db_company = session.exec(select(Company).where(Company.id == company_id)).first()
        if not db_company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada.")

        session.delete(db_company)
        session.commit()
        return {"ok": True, "message": "Empresa deletada com sucesso"}
        
 