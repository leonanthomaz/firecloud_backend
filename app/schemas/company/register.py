from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

from app.enums.register import RegisterStatusEnum

class RegisterRequest(BaseModel):
    """
    Esquema para criação de um pré-cadastro de empresa.
    """
    
    email: EmailStr  # E-mail para contato
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None    
    username: str
    password_hash: str
    is_admin: Optional[bool] = None
    is_register_google: Optional[bool] = None
    
    company_name: Optional[str] = None  # Nome da empresa
    cnpj: Optional[str] = None  # CNPJ (se aplicável)
    business_type: Optional[str] = None  # Tipo de serviço ofertado - service, product, service_product
    industry: Optional[str] = None # Ramo de atuação
    phone: Optional[str] = None  # Telefone para contato
    website: Optional[str] = None  # Site da empresa
    
    assistant_preference: Optional[str] = None  # Preferências de assistente

    plan_interest: Optional[str] = None  # Plano desejado
    
    privacy_policy_version: Optional[str] = None
    privacy_policy_accepted_at: Optional[datetime] = None
    additional_info: Optional[str] = None  # Informações adicionais fornecidas pelo usuário
    
class RegisterUpdate(BaseModel):
    company_name: Optional[str] = None  # Nome da empresa
    cnpj: Optional[str] = None  # CNPJ (se aplicável)
    business_type: Optional[str] = None  # Tipo de negócio
    industry: Optional[str] = None # Ramo de atuação
    phone: Optional[str] = None  # Telefone para contato
    website: Optional[str] = None  # Site da empresa
    
    assistant_preference: Optional[str] = None  # Preferências de assistente

    plan_interest: Optional[str] = None  # Plano desejado
    
    privacy_policy_version: Optional[str] = None
    privacy_policy_accepted_at: Optional[datetime] = None
    additional_info: Optional[str] = None  # Informações adicionais fornecidas pelo usuário
    
class RegisterResponse(RegisterRequest):
    """
    Esquema para resposta de um pré-cadastro de empresa.
    """
    id: int
    status: RegisterStatusEnum
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
