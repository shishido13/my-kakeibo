from datetime import date
from sqlmodel import Session, select, func
from typing import Dict, Any

from app.models.transaction import Transaction
from app.models.category import Category

def get_monthly_summary(db: Session, year: int, month: int) -> Dict[str, Any]:
    """
    指定された年月の集計データを取得する
    - 総支出額
    - カテゴリ別の支出額
    """
    
    # SQLiteの日付関数を使って年月でフィルタリングする
    # transaction.date は "YYYY-MM-DD" 形式の文字列として保存されている前提
    month_str = f"{year:04d}-{month:02d}"
    
    # 1. 指定月の総支出
    # func.sum() を使って合計を計算
    total_amount_stmt = select(func.sum(Transaction.amount)).where(
        Transaction.date.startswith(month_str)
    )
    total_result = db.exec(total_amount_stmt).first()
    total_amount = total_result if total_result is not None else 0

    # 2. カテゴリ別の集計
    category_stmt = (
        select(Category.name, func.sum(Transaction.amount))
        .join(Category, Transaction.category_id == Category.id)
        .where(Transaction.date.startswith(month_str))
        .group_by(Category.name)
    )
    
    category_results = db.exec(category_stmt).all()
    
    categories_breakdown = [
        {"category_name": name, "amount": amount} 
        for name, amount in category_results
    ]

    return {
        "year": year,
        "month": month,
        "total_amount": total_amount,
        "categories_breakdown": categories_breakdown
    }
