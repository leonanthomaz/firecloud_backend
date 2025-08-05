from pydantic import BaseModel
from typing import Optional, Literal

class FinanceCategoryBase(BaseModel):
    name: str
    type: Literal["revenue", "expense"]  # evita erro de string qualquer
    description: Optional[str] = None

class FinanceCategoryCreate(FinanceCategoryBase):
    pass

class FinanceCategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[Literal["revenue", "expense"]] = None
    description: Optional[str] = None

class FinanceCategoryRead(FinanceCategoryBase):
    id: int

    class Config:
        orm_mode = True
