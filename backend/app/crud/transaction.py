from datetime import date, datetime
from typing import List, Optional

from app.db.session import DatabaseSession
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate


def _row_to_transaction(row: dict | None) -> Optional[TransactionRead]:
    return TransactionRead.model_validate(row) if row else None


def _serialize_date(value: date) -> str:
    return value.isoformat()


def _escape_text(value: str) -> str:
    return value.replace("'", "''")


def _build_transaction_conditions(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_ids: Optional[List[int]] = None,
    expense_type_id: Optional[int] = None,
    payer: Optional[str] = None,
    keyword: Optional[str] = None,
    table_alias: str = ''
) -> list[str]:
    prefix = f'{table_alias}.' if table_alias else ''
    conditions: list[str] = []

    if start_date:
        conditions.append(f"{prefix}date >= '{_serialize_date(start_date)}'")
    if end_date:
        conditions.append(f"{prefix}date <= '{_serialize_date(end_date)}'")
    if category_ids:
        category_list = ', '.join(str(category_id) for category_id in category_ids)
        conditions.append(f"{prefix}category_id IN ({category_list})")
    if expense_type_id:
        conditions.append(f"{prefix}expense_type_id = {expense_type_id}")
    if payer:
        conditions.append(f"{prefix}payer = '{_escape_text(payer)}'")
    if keyword:
        escaped_keyword = _escape_text(keyword)
        conditions.append(
            "(" 
            f"{prefix}shop LIKE '%{escaped_keyword}%' OR "
            f"{prefix}content LIKE '%{escaped_keyword}%' OR "
            f"COALESCE({prefix}description, '') LIKE '%{escaped_keyword}%'"
            ")"
        )

    return conditions


def get_transaction(session: DatabaseSession, transaction_id: int) -> Optional[TransactionRead]:
    row = session.fetch_one(
        "SELECT t.id, t.date, t.amount, t.category_id, t.expense_type_id, et.name AS expense_type_name, "
        "t.shop, t.content, t.payer, t.description, t.source_type, t.created_at "
        "FROM t_transaction t "
        "JOIN m_expense_type et ON et.id = t.expense_type_id "
        f"WHERE t.id = {transaction_id}"
    )
    return _row_to_transaction(row)

def get_transactions(
    session: DatabaseSession,
    skip: int = 0, 
    limit: int = 1000,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_ids: Optional[List[int]] = None,
    expense_type_id: Optional[int] = None,
    payer: Optional[str] = None,
    keyword: Optional[str] = None
) -> List[TransactionRead]:
    conditions = _build_transaction_conditions(
        start_date=start_date,
        end_date=end_date,
        category_ids=category_ids,
        expense_type_id=expense_type_id,
        payer=payer,
        keyword=keyword,
    )

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ''
    rows = session.fetch_all(
        "SELECT t.id, t.date, t.amount, t.category_id, t.expense_type_id, et.name AS expense_type_name, "
        "t.shop, t.content, t.payer, t.description, t.source_type, t.created_at "
        "FROM t_transaction t "
        "JOIN m_expense_type et ON et.id = t.expense_type_id "
        f"{where_clause} ORDER BY t.date DESC, t.id DESC LIMIT {limit} OFFSET {skip}"
    )
    return [TransactionRead.model_validate(row) for row in rows]

def get_analytics_summary(
    session: DatabaseSession,
    start_date: date,
    end_date: date,
    category_ids: Optional[List[int]] = None,
    expense_type_id: Optional[int] = None,
    payer: Optional[str] = None,
    prev_start_date: Optional[date] = None,
    prev_end_date: Optional[date] = None
):
    current_conditions = _build_transaction_conditions(
        start_date=start_date,
        end_date=end_date,
        category_ids=category_ids,
        expense_type_id=expense_type_id,
        payer=payer,
        table_alias='t'
    )
    current_where_clause = f"WHERE {' AND '.join(current_conditions)}" if current_conditions else ''

    current_total = session.fetch_scalar(
        "SELECT COALESCE(SUM(amount), 0) AS total_amount "
        "FROM t_transaction t "
        f"{current_where_clause}"
    ) or 0

    categories = session.fetch_all(
        "SELECT c.id AS category_id, c.name AS category_name, COALESCE(SUM(t.amount), 0) AS amount "
        "FROM m_category c "
        "JOIN t_transaction t ON t.category_id = c.id "
        f"{current_where_clause} "
        "GROUP BY c.id, c.name ORDER BY amount DESC"
    )

    payers = session.fetch_all(
        "SELECT payer, COALESCE(SUM(amount), 0) AS amount "
        "FROM t_transaction t "
        f"{current_where_clause} "
        "GROUP BY payer ORDER BY amount DESC"
    )

    prev_total = 0
    if prev_start_date and prev_end_date:
        previous_conditions = _build_transaction_conditions(
            start_date=prev_start_date,
            end_date=prev_end_date,
            category_ids=category_ids,
            expense_type_id=expense_type_id,
            payer=payer,
            table_alias='t'
        )
        previous_where_clause = f"WHERE {' AND '.join(previous_conditions)}" if previous_conditions else ''
        prev_total = session.fetch_scalar(
            "SELECT COALESCE(SUM(amount), 0) AS total_amount "
            "FROM t_transaction t "
            f"{previous_where_clause}"
        ) or 0

    comparison_percentage = None
    if prev_total > 0:
        comparison_percentage = ((current_total - prev_total) / prev_total) * 100

    return {
        "total_amount": current_total,
        "categories": categories,
        "payers": payers,
        "previous_total_amount": prev_total,
        "comparison_percentage": comparison_percentage
    }

def get_analytics_trend(
    session: DatabaseSession,
    start_date: date,
    end_date: date,
    group_by_type: str, # "day", "week", "month"
    category_ids: Optional[List[int]] = None,
    expense_type_id: Optional[int] = None,
    payer: Optional[str] = None,
):
    if group_by_type == "day":
        date_format = "%Y-%m-%d"
    elif group_by_type == "week":
        # Turso/libsql uses SQLite date functions, so year-week text grouping is sufficient here.
        date_format = "%Y-W%W"
    else: # month
        date_format = "%Y-%m"

    conditions = _build_transaction_conditions(
        start_date=start_date,
        end_date=end_date,
        category_ids=category_ids,
        expense_type_id=expense_type_id,
        payer=payer,
    )
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ''

    trend_rows = session.fetch_all(
        "SELECT strftime('{fmt}', date) AS label, COALESCE(SUM(amount), 0) AS amount "
        "FROM t_transaction "
        "{where_clause} "
        "GROUP BY strftime('{fmt}', date) "
        "ORDER BY label"
        .format(
            fmt=date_format,
            where_clause=where_clause,
        )
    )

    return trend_rows


def create_transaction(session: DatabaseSession, transaction_in: TransactionCreate) -> TransactionRead:
    created_at = datetime.utcnow()
    transaction_id = session.insert(
        't_transaction',
        {
            'date': transaction_in.date,
            'amount': transaction_in.amount,
            'category_id': transaction_in.category_id,
            'expense_type_id': transaction_in.expense_type_id,
            'shop': transaction_in.shop,
            'content': transaction_in.content,
            'payer': transaction_in.payer,
            'description': transaction_in.description,
            'source_type': transaction_in.source_type or 'manual',
            'created_at': created_at,
        },
    )
    return get_transaction(session, int(transaction_id))


def update_transaction(session: DatabaseSession, transaction_id: int, transaction_in: TransactionUpdate) -> Optional[TransactionRead]:
    existing = get_transaction(session, transaction_id)
    if not existing:
        return None

    updates = transaction_in.model_dump(exclude_unset=True)
    session.update('t_transaction', transaction_id, updates)
    return get_transaction(session, transaction_id)


def delete_transaction(session: DatabaseSession, transaction_id: int) -> bool:
    existing = get_transaction(session, transaction_id)
    if not existing:
        return False

    session.delete('t_transaction', transaction_id)
    return True
