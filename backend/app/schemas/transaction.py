from datetime import date as DateType, datetime as DateTimeType
from typing import Optional, Literal
from pydantic import BaseModel

class TransactionCreate(BaseModel):
    date: DateType
    amount: int
    category_id: int
    expense_type_id: Literal[1, 2] = 1
    shop: str
    content: str
    payer: str
    description: Optional[str] = None
    source_type: Optional[Literal["manual", "ai_pdf", "csv_import"]] = "manual"

class TransactionUpdate(BaseModel):
    date: Optional[DateType] = None
    amount: Optional[int] = None
    category_id: Optional[int] = None
    expense_type_id: Optional[Literal[1, 2]] = None
    shop: Optional[str] = None
    content: Optional[str] = None
    payer: Optional[str] = None
    description: Optional[str] = None
    source_type: Optional[Literal["manual", "ai_pdf", "csv_import"]] = None

class TransactionRead(BaseModel):
    id: int
    date: DateType
    amount: int
    category_id: int
    expense_type_id: int
    expense_type_name: str
    shop: str
    content: str
    payer: str
    description: Optional[str] = None
    source_type: str
    created_at: DateTimeType
