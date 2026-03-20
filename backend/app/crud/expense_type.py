from typing import List

from app.db.session import DatabaseSession
from app.schemas.expense_type import ExpenseTypeRead


def get_expense_types(session: DatabaseSession) -> List[ExpenseTypeRead]:
    rows = session.fetch_all(
        "SELECT id, name FROM m_expense_type ORDER BY id"
    )
    return [ExpenseTypeRead.model_validate(row) for row in rows]