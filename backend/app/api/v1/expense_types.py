from typing import List

from fastapi import APIRouter, Depends

from app.crud import expense_type as crud_expense_type
from app.db.session import DatabaseSession, get_session
from app.schemas.expense_type import ExpenseTypeRead

router = APIRouter()


@router.get("/", response_model=List[ExpenseTypeRead])
def read_expense_types(session: DatabaseSession = Depends(get_session)):
    return crud_expense_type.get_expense_types(session)