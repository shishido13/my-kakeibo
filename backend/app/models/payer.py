from sqlmodel import SQLModel, Field

class PayerBase(SQLModel):
    name: str = Field(index=True)
    is_active: bool = Field(default=True)

class Payer(PayerBase, table=True):
    __tablename__ = "m_payer"
    id: int | None = Field(default=None, primary_key=True)
