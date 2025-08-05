from datetime import datetime, timedelta, timezone
import logging
from typing import List
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlmodel import Session, select

from app.auth.auth import AuthRouter
from app.configuration.settings import Configuration
from app.middleware.admin import is_admin
from app.models.company.address import Address
from app.models.company.company import Company
from app.models.plan.plan import Plan
from app.models.user.user import User
from app.schemas.company.company import CompanyRequest, CompanyStatusResponse, CompanyStatusUpdate, CompanyUpdate
from app.database.connection import get_session
from app.services.email import EmailService
from app.utils.company_utils import remove_logo_company, upload_logo_company
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
        super().__init__(prefix="/company", *args, **kwargs)

        self.add_api_route("/all", self.get_all_companies, methods=["GET"], response_model=List[Company])
        self.add_api_route("/create", self.create_company, methods=["POST"], response_model=Company)
        self.add_api_route("/recent-companies", self.get_recent_companies, methods=["GET"], response_model=dict)
        self.add_api_route("/status", self.change_company_status, methods=["POST"], response_model=CompanyStatusResponse)
        self.add_api_route("/code/{code}", self.get_company_for_chat, methods=["GET"], response_model=Company)
        self.add_api_route("/{company_id}", self.get_company, methods=["GET"], response_model=Company)
        self.add_api_route("/{company_id}", self.update_company, methods=["PUT"], response_model=Company)
        self.add_api_route("/{company_id}", self.delete_company, methods=["DELETE"], response_model=dict)
        self.add_api_route("/{company_id}/upload-logo", self.upload_logo, methods=["POST"], response_model=dict)
        self.add_api_route("/{company_id}/remove-logo", self.remove_logo, methods=["DELETE"], response_model=dict)
        self.add_api_route("/{company_id}/associate-plan/{plan_id}", self.associate_plan, methods=["PUT"])
        self.add_api_route("/tutorial/{company_id}", self.change_tutorial, methods=["PUT"])

    def get_company_for_chat(self, code: str, session: Session = Depends(db_session)):
        """
        Retorna os dados de uma empresa cadastrada pelo ID.
        """
        company = session.exec(select(Company).where(Company.code == code)).first()

        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada.")
        return company

    def get_company(self, company_id: int, session: Session = Depends(db_session)):
        """
        Retorna os dados de uma empresa cadastrada pelo ID.
        """
        logging.info(f"EMPRESA ID >>>> {company_id}")

        company = session.exec(select(Company).where(Company.id == company_id)).first()
        logging.info(f"EMPRESA ENCONTRADA >>>> {company}")
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada.")
        return company

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

        # Cria a empresa primeiro
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
            status=data.status,
            social_media_links=data.social_media_links,
            contact_email=data.contact_email,
            business_type=data.business_type,
            is_new_company = True,
            tutorial_completed = False
        )
                
        if not db_company.code:
            db_company.code = generate_hash(str(uuid.uuid4()))

        try:
            session.add(db_company)
            session.commit()
            session.refresh(db_company)

        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        return db_company

    def update_company(
        self,
        company_id: int,
        company: CompanyUpdate,
        session: Session = Depends(db_session),
    ):

        db_company = session.exec(select(Company).where(Company.id == company_id)).first()

        if not db_company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada.")

        # Atualiza os dados da empresa
        company_data = company.dict(exclude_unset=True, exclude={"addresses"})
        for key, value in company_data.items():
            setattr(db_company, key, value)

        # Atualiza/Cria/Remove endereços, se vierem
        if company.addresses is not None:
            new_addresses = []

            for addr in company.addresses:
                if addr.id:
                    db_address = session.exec(select(Address).where(Address.id == addr.id, Address.company_id == company_id)).first()
                    if db_address:
                        for key, value in addr.dict(exclude_unset=True).items():
                            setattr(db_address, key, value)
                        new_addresses.append(db_address)
                    else:
                        raise HTTPException(status_code=404, detail=f"Endereço com ID {addr.id} não encontrado para esta empresa.")
                else:
                    new_address = Address(**addr.dict(exclude_unset=True))
                    new_address.company_id = company_id
                    session.add(new_address)
                    session.flush()  # Garante que o ID seja criado
                    new_addresses.append(new_address)

            # Remove endereços que não estão mais presentes
            existing_ids = [a.id for a in new_addresses if a.id]
            db_existing_addresses = session.exec(select(Address).where(Address.company_id == company_id)).all()
            for db_addr in db_existing_addresses:
                if db_addr.id not in existing_ids:
                    session.delete(db_addr)

            db_company.addresses = new_addresses

        db_company.updated_at = datetime.now(timezone.utc)

        session.add(db_company)
        session.commit()
        session.refresh(db_company)

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
        
    async def upload_logo(self, company_id: int, image_file: UploadFile = File(...), session: Session = Depends(db_session)):
        company = session.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")

        # Remove o logo anterior, se houver
        if company.logo_url:
            remove_logo_company(company.logo_url)

        result = await upload_logo_company(image_file)

        company.logo_url = result["url"]
        session.add(company)
        session.commit()
        session.refresh(company)

        return {"message": "Logo enviado com sucesso", "url": result["url"]}
    
    def remove_logo(self, company_id: int, session: Session = Depends(db_session)):
        company = session.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")

        if not company.logo_url:
            raise HTTPException(status_code=400, detail="Empresa não possui logo para remover")

        remove_logo_company(company.logo_url)

        company.logo_url = None
        session.add(company)
        session.commit()
        session.refresh(company)

        return {"message": "Logo removido com sucesso"}

    def get_recent_companies(self, session: Session = Depends(db_session)):
        now = datetime.now(timezone.utc)
        start_of_week = now - timedelta(days=now.weekday())
        start_of_month = now.replace(day=1)

        recent_companies_week = session.exec(select(Company).where(Company.created_at >= start_of_week)).all()
        recent_companies_month = session.exec(select(Company).where(Company.created_at >= start_of_month)).all()

        return {
            "week": recent_companies_week,
            "month": recent_companies_month
        }

    def associate_plan(self, company_id: int, plan_id: int, session: Session = Depends(db_session)):
        """
        Associa um plano a uma empresa.
        """
        company = session.exec(select(Company).where(Company.id == company_id)).first()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada.")

        plan = session.exec(select(Plan).where(Plan.id == plan_id)).first()
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plano não encontrado.")

        company.plan_id = plan.id
        company.updated_at = datetime.now(timezone.utc)

        session.add(company)
        session.commit()
        session.refresh(company)

        return {"message": "Plano associado com sucesso", "company": company}
    
    async def change_company_status(
        self,
        payload: CompanyStatusUpdate,
        session: Session = Depends(db_session)
    ) -> CompanyStatusResponse:
        """Atualiza o status da empresa com tratamento completo"""
        company = session.exec(select(Company).order_by(Company.updated_at.desc())).first()
        
        try:
            company.is_open = payload.new_status
            company.updated_at = datetime.now(timezone.utc)
            session.add(company)
            session.commit()
            session.refresh(company)
            
            return CompanyStatusResponse(
                current_status=company.is_open,
                message=f"Status da empresa atualizado para: {company.status}"
            )
            
        except Exception as e:
            session.rollback()
            logging.error(f"Erro ao atualizar status da empresa: {str(e)}", exc_info=True)
            raise Exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao persistir alteração de status",
                solution="Tente novamente mais tarde."
            )
            
    async def change_tutorial(
        self,
        company_id: int,
        session: Session = Depends(db_session)
    ):
        """
        Atualiza o atributo 'is_new_company' para False e 'tutorial_completed' para True para a empresa especificada.
        """
        try:
            company = session.exec(select(Company).where(Company.id == company_id)).first()

            if not company:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada.")

            company.is_new_company = False
            company.tutorial_completed = True
            company.updated_at = datetime.now(timezone.utc)

            session.add(company)
            session.commit()
            session.refresh(company)

            return {"message": "Empresa marcada como não-nova com sucesso", "company": company}

        except Exception as e:
            session.rollback()
            logging.error(f"Erro ao atualizar 'is_new_company': {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar status de nova empresa. Tente novamente."
            )
