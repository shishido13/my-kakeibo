from datetime import date, datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class TransactionBase(SQLModel):
    date: date
    amount: int
    category_id: int = Field(foreign_key="m_category.id")
    shop: str
    content: str
    payer: str
    description: Optional[str] = None
    source_type: str = Field(default="manual")

class Transaction(TransactionBase, table=True):
    __tablename__ = "t_transaction"
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
