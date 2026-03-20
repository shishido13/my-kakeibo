from datetime import date, datetime
from typing import List, Optional

from app.db.session import DatabaseSession
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate


def _row_to_transaction(row: dict | None) -> Optional[Transaction]:
    return Transaction.model_validate(row) if row else None


def _serialize_date(value: date) -> str:
    return value.isoformat()


def _escape_text(value: str) -> str:
    return value.replace("'", "''")


def get_transaction(session: DatabaseSession, transaction_id: int) -> Optional[Transaction]:
    row = session.fetch_one(
        f"SELECT id, date, amount, category_id, shop, content, payer, description, source_type, created_at FROM t_transaction WHERE id = {transaction_id}"
    )
    return _row_to_transaction(row)

def get_transactions(
    session: DatabaseSession,
    skip: int = 0, 
    limit: int = 1000,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_ids: Optional[List[int]] = None,
    payer: Optional[str] = None,
    keyword: Optional[str] = None
) -> List[Transaction]:
    conditions: list[str] = []

    if start_date:
        conditions.append(f"date >= '{_serialize_date(start_date)}'")
    if end_date:
        conditions.append(f"date <= '{_serialize_date(end_date)}'")
    if category_ids:
        category_list = ', '.join(str(category_id) for category_id in category_ids)
        conditions.append(f"category_id IN ({category_list})")
    if payer:
        conditions.append(f"payer = '{_escape_text(payer)}'")
    if keyword:
        escaped_keyword = _escape_text(keyword)
        conditions.append(
            "(" 
            f"shop LIKE '%{escaped_keyword}%' OR "
            f"content LIKE '%{escaped_keyword}%' OR "
            f"COALESCE(description, '') LIKE '%{escaped_keyword}%'"
            ")"
        )

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ''
    rows = session.fetch_all(
        "SELECT id, date, amount, category_id, shop, content, payer, description, source_type, created_at "
        f"FROM t_transaction {where_clause} ORDER BY date DESC, id DESC LIMIT {limit} OFFSET {skip}"
    )
    return [Transaction.model_validate(row) for row in rows]

def get_analytics_summary(
    session: DatabaseSession,
    start_date: date,
    end_date: date,
    prev_start_date: Optional[date] = None,
    prev_end_date: Optional[date] = None
):
    start_literal = _serialize_date(start_date)
    end_literal = _serialize_date(end_date)

    current_total = session.fetch_scalar(
        "SELECT COALESCE(SUM(amount), 0) AS total_amount "
        f"FROM t_transaction WHERE date >= '{start_literal}' AND date <= '{end_literal}'"
    ) or 0

    categories = session.fetch_all(
        "SELECT c.id AS category_id, c.name AS category_name, COALESCE(SUM(t.amount), 0) AS amount "
        "FROM m_category c "
        "JOIN t_transaction t ON t.category_id = c.id "
        f"WHERE t.date >= '{start_literal}' AND t.date <= '{end_literal}' "
        "GROUP BY c.id, c.name ORDER BY amount DESC"
    )

    payers = session.fetch_all(
        "SELECT payer, COALESCE(SUM(amount), 0) AS amount "
        f"FROM t_transaction WHERE date >= '{start_literal}' AND date <= '{end_literal}' "
        "GROUP BY payer ORDER BY amount DESC"
    )

    prev_total = 0
    if prev_start_date and prev_end_date:
        prev_total = session.fetch_scalar(
            "SELECT COALESCE(SUM(amount), 0) AS total_amount "
            f"FROM t_transaction WHERE date >= '{_serialize_date(prev_start_date)}' AND date <= '{_serialize_date(prev_end_date)}'"
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
    group_by_type: str # "day", "week", "month"
):
    if group_by_type == "day":
        date_format = "%Y-%m-%d"
    elif group_by_type == "week":
        # Turso/libsql uses SQLite date functions, so year-week text grouping is sufficient here.
        date_format = "%Y-W%W"
    else: # month
        date_format = "%Y-%m"

    trend_rows = session.fetch_all(
        "SELECT strftime('{fmt}', date) AS label, COALESCE(SUM(amount), 0) AS amount "
        "FROM t_transaction "
        "WHERE date >= '{start}' AND date <= '{end}' "
        "GROUP BY strftime('{fmt}', date) "
        "ORDER BY label"
        .format(
            fmt=date_format,
            start=_serialize_date(start_date),
            end=_serialize_date(end_date),
        )
    )

    return trend_rows


def create_transaction(session: DatabaseSession, transaction_in: TransactionCreate) -> Transaction:
    created_at = datetime.utcnow()
    transaction_id = session.insert(
        't_transaction',
        {
            'date': transaction_in.date,
            'amount': transaction_in.amount,
            'category_id': transaction_in.category_id,
            'shop': transaction_in.shop,
            'content': transaction_in.content,
            'payer': transaction_in.payer,
            'description': transaction_in.description,
            'source_type': transaction_in.source_type or 'manual',
            'created_at': created_at,
        },
    )
    return get_transaction(session, int(transaction_id))


def update_transaction(session: DatabaseSession, transaction_id: int, transaction_in: TransactionUpdate) -> Optional[Transaction]:
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
