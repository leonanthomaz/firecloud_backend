# app/schemas/company.py

from datetime import time
from typing import List, Optional
from pydantic import BaseModel, Field

from app.enums.company import CompanyOpenEnum, CompanyStatusEnum
from app.schemas.company.address import AddressUpdate 

class CompanyBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    industry: Optional[str] = Field(None, max_length=255)
    
    addresses: Optional[List[AddressUpdate]] = None

    cnpj: Optional[str] = Field(None, max_length=20)
    phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=255)
    
    is_open: Optional[CompanyOpenEnum] = CompanyOpenEnum.CLOSE
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    working_days: Optional[List[str]] = None

    status: Optional[CompanyStatusEnum] = CompanyStatusEnum.PENDING
    social_media_links: Optional[dict[str, str]] = None
    contact_email: Optional[str] = None
    business_type: Optional[str] = Field(None, max_length=50)

class CompanyRequest(CompanyBase):
    pass

class CompanyUpdate(CompanyBase):
    assistant_link: Optional[str] = None

class CompanyPublicInfo(CompanyBase):
    code: str

class CompanyStatusUpdate(BaseModel):
    new_status: CompanyOpenEnum

class CompanyStatusResponse(BaseModel):
    current_status: CompanyOpenEnum
    message: Optional[str] = None
