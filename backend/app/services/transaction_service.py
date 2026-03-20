from calendar import monthrange
from datetime import date
from typing import Any, Dict

from app.db.session import DatabaseSession

def get_monthly_summary(db: DatabaseSession, year: int, month: int) -> Dict[str, Any]:
    """
    指定された年月の集計データを取得する
    - 総支出額
    - カテゴリ別の支出額
    """
    
    month_start = date(year, month, 1)
    month_end = date(year, month, monthrange(year, month)[1])
    
    total_amount = db.fetch_scalar(
        "SELECT COALESCE(SUM(amount), 0) AS total_amount "
        f"FROM t_transaction WHERE date >= '{month_start.isoformat()}' AND date <= '{month_end.isoformat()}'"
    ) or 0

    category_results = db.fetch_all(
        "SELECT c.name AS category_name, COALESCE(SUM(t.amount), 0) AS amount "
        "FROM m_category c "
        "JOIN t_transaction t ON t.category_id = c.id "
        f"WHERE t.date >= '{month_start.isoformat()}' AND t.date <= '{month_end.isoformat()}' "
        "GROUP BY c.name ORDER BY amount DESC"
    )

    categories_breakdown = [
        {"category_name": row["category_name"], "amount": row["amount"]}
        for row in category_results
    ]

    return {
        "year": year,
        "month": month,
        "total_amount": total_amount,
        "categories_breakdown": categories_breakdown
    }
