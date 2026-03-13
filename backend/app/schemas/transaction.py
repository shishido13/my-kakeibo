from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel

class TransactionCreate(BaseModel):
    date: date
    amount: int
    category_id: int
    shop: str
    content: str
    payer: str
    description: Optional[str] = None
    source_type: Optional[str] = "manual"

class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    amount: Optional[int] = None
    category_id: Optional[int] = None
    shop: Optional[str] = None
    content: Optional[str] = None
    payer: Optional[str] = None
    description: Optional[str] = None
    source_type: Optional[str] = None

class TransactionRead(BaseModel):
    id: int
    date: date
    amount: int
    category_id: int
    shop: str
    content: str
    payer: str
    description: Optional[str] = None
    source_type: str
    created_at: datetime
