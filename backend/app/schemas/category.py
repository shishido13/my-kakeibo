from typing import Optional
from pydantic import BaseModel

class CategoryCreate(BaseModel):
    name: str

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class CategoryRead(BaseModel):
    id: int
    name: str
    is_active: bool
