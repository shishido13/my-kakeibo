from sqlmodel import Field, SQLModel


class ExpenseType(SQLModel, table=True):
    __tablename__ = "m_expense_type"

    id: int = Field(primary_key=True)
    name: str