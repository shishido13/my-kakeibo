from typing import Optional
from pydantic import BaseModel

class PayerCreate(BaseModel):
    name: str

class PayerUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class PayerRead(BaseModel):
    id: int
    name: str
    is_active: bool
