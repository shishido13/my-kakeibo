from pydantic import BaseModel


class ExpenseTypeRead(BaseModel):
    id: int
    name: str