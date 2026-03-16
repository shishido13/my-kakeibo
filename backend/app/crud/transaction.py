from datetime import date
from typing import List, Optional
from sqlalchemy import func
from sqlmodel import Session, select
from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.transaction import TransactionCreate, TransactionUpdate

def get_transaction(session: Session, transaction_id: int) -> Optional[Transaction]:
    return session.get(Transaction, transaction_id)

def get_transactions(
    session: Session, 
    skip: int = 0, 
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_ids: Optional[List[int]] = None,
    payer: Optional[str] = None,
    keyword: Optional[str] = None
) -> List[Transaction]:
    query = select(Transaction)
    
    if start_date:
        query = query.where(Transaction.date >= start_date)
    if end_date:
        query = query.where(Transaction.date <= end_date)
    if category_ids:
        query = query.where(Transaction.category_id.in_(category_ids))
    if payer:
        query = query.where(Transaction.payer == payer)
    if keyword:
        # Simple simple search in shop, content, description
        query = query.where(
            (Transaction.shop.contains(keyword)) | 
            (Transaction.content.contains(keyword)) | 
            (Transaction.description.contains(keyword))
        )
        
    query = query.order_by(Transaction.date.desc()).offset(skip).limit(limit)
    return session.exec(query).all()

def get_analytics_summary(
    session: Session,
    start_date: date,
    end_date: date,
    prev_start_date: Optional[date] = None,
    prev_end_date: Optional[date] = None
):
    # Current period summary
    current_total = session.exec(
        select(func.sum(Transaction.amount))
        .where(Transaction.date >= start_date)
        .where(Transaction.date <= end_date)
    ).first() or 0

    # Category breakdown
    categories = session.exec(
        select(Category.id, Category.name, func.sum(Transaction.amount).label("amount"))
        .join(Transaction, Transaction.category_id == Category.id)
        .where(Transaction.date >= start_date)
        .where(Transaction.date <= end_date)
        .group_by(Category.id, Category.name)
        .order_by(func.sum(Transaction.amount).desc())
    ).all()

    # Payer breakdown
    payers = session.exec(
        select(Transaction.payer, func.sum(Transaction.amount).label("amount"))
        .where(Transaction.date >= start_date)
        .where(Transaction.date <= end_date)
        .group_by(Transaction.payer)
        .order_by(func.sum(Transaction.amount).desc())
    ).all()

    # Previous period comparison
    prev_total = 0
    if prev_start_date and prev_end_date:
        prev_total = session.exec(
            select(func.sum(Transaction.amount))
            .where(Transaction.date >= prev_start_date)
            .where(Transaction.date <= prev_end_date)
        ).first() or 0

    comparison_percentage = None
    if prev_total > 0:
        comparison_percentage = ((current_total - prev_total) / prev_total) * 100

    return {
        "total_amount": current_total,
        "categories": [{"category_id": c[0], "category_name": c[1], "amount": c[2]} for c in categories],
        "payers": [{"payer": p[0], "amount": p[1]} for p in payers],
        "previous_total_amount": prev_total,
        "comparison_percentage": comparison_percentage
    }

def get_analytics_trend(
    session: Session,
    start_date: date,
    end_date: date,
    group_by_type: str # "day", "week", "month"
):
    # This is a simplified version. For SQLite/Postgres differences, 
    # we might need to use different date formatting strings.
    # Assuming SQLite for now based on common patterns.
    
    if group_by_type == "day":
        date_format = "%Y-%m-%d"
    elif group_by_type == "week":
        # SQLite doesn't have a direct week-of-year that is easy for group by, 
        # using year-week format
        date_format = "%Y-W%W"
    else: # month
        date_format = "%Y-%m"

    trend_data = session.exec(
        select(func.strftime(date_format, Transaction.date), func.sum(Transaction.amount))
        .where(Transaction.date >= start_date)
        .where(Transaction.date <= end_date)
        .group_by(func.strftime(date_format, Transaction.date))
        .order_by(Transaction.date)
    ).all()

    return [{"label": t[0], "amount": t[1]} for t in trend_data]

def create_transaction(session: Session, transaction_in: TransactionCreate) -> Transaction:
    db_transaction = Transaction.model_validate(transaction_in)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction

def update_transaction(session: Session, db_transaction: Transaction, transaction_in: TransactionUpdate) -> Transaction:
    transaction_data = transaction_in.model_dump(exclude_unset=True)
    for key, value in transaction_data.items():
        setattr(db_transaction, key, value)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction

def delete_transaction(session: Session, db_transaction: Transaction) -> Transaction:
    session.delete(db_transaction)
    session.commit()
    return db_transaction
