from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=255)
    is_register_google: Optional[bool] = None

class UserCreate(UserBase):
    email: EmailStr
    password: str
    company_id: Optional[int] = None
    is_admin: Optional[bool] = None

class UserUpdate(UserBase):
    is_admin: Optional[bool] = None
    company_id: Optional[int] = None
    password: Optional[str] = None

class UserUpdateCustomer(BaseModel):
    first_name: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=255)
    is_admin: Optional[bool] = None

class UserCredentials(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    email: EmailStr
    company_id: Optional[int] = None
    is_admin: bool
    
class UserPasswordUpdate(BaseModel):
    current_password: str | None = None
    new_password: str = Field(..., min_length=6)