from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.models.company.company import Company
from app.models.service.service import Service
from app.models.service.category_service import CategoryService
from app.auth.auth import AuthRouter
from app.database.connection import get_session
from app.schemas.service.service import (
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
)

db_session = get_session
get_current_user = AuthRouter().get_current_user

class ServiceRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/services/{company_id}/", self.list_services, methods=["GET"], response_model=List[ServiceResponse])
        self.add_api_route("/services/{company_id}/", self.create_service, methods=["POST"], response_model=ServiceResponse)
        self.add_api_route("/services/{company_id}/{service_id}", self.get_service, methods=["GET"], response_model=ServiceResponse)
        self.add_api_route("/services/{company_id}/{service_id}", self.update_service, methods=["PUT"], response_model=ServiceResponse)
        self.add_api_route("/services/{company_id}/{service_id}", self.delete_service, methods=["DELETE"], response_model=dict)

    def list_services(self, company_id: int, session: Session = Depends(db_session)):
        company = session.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")

        services = session.exec(select(Service).where(Service.company_id == company_id)).all()
        return services

    def get_service(self, company_id: int, service_id: int, session: Session = Depends(db_session)):
        company = session.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")
        
        service = session.exec(
            select(Service).where(Service.id == service_id, Service.company_id == company_id)
        ).first()
        if not service:
            raise HTTPException(status_code=404, detail="Serviço não encontrado ou não pertence à empresa")

        return service

    def create_service(
        self,
        company_id: int,
        service_data: ServiceCreate,
        session: Session = Depends(db_session),
    ):
        company = session.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=400, detail="Empresa não encontrada")

        category = session.get(CategoryService, service_data.category_id)
        if not category:
            raise HTTPException(status_code=400, detail="Categoria não encontrada")

        service = Service(**service_data.dict(exclude={"company_id"}), company_id=company_id)
        session.add(service)
        session.commit()
        session.refresh(service)
        return service

    def update_service(
        self,
        company_id: int,
        service_id: int,
        updated_data: ServiceUpdate,
        session: Session = Depends(db_session),
    ):
        company = session.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")
        
        service = session.exec(
            select(Service).where(Service.id == service_id, Service.company_id == company_id)
        ).first()
        if not service:
            raise HTTPException(status_code=404, detail="Serviço não encontrado ou não pertence à empresa")

        if updated_data.category_id and updated_data.category_id != service.category_id:
            category = session.get(CategoryService, updated_data.category_id)
            if not category:
                raise HTTPException(status_code=400, detail="Categoria não encontrada")
            service.category_id = updated_data.category_id

        for key, value in updated_data.dict(exclude_unset=True).items():
            setattr(service, key, value)

        session.add(service)
        session.commit()
        session.refresh(service)
        return service

    def delete_service(
        self,
        company_id: int,
        service_id: int,
        session: Session = Depends(db_session),
    ):
        company = session.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")

        service = session.exec(
            select(Service).where(Service.id == service_id, Service.company_id == company_id)
        ).first()
        if not service:
            raise HTTPException(status_code=404, detail="Serviço não encontrado ou não pertence à empresa")

        session.delete(service)
        session.commit()
        return {"message": "Serviço deletado com sucesso"}
