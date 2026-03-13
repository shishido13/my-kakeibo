from datetime import date
from typing import List, Optional
from sqlmodel import Session, select
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate

def get_transaction(session: Session, transaction_id: int) -> Optional[Transaction]:
    return session.get(Transaction, transaction_id)

def get_transactions(
    session: Session, 
    skip: int = 0, 
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None,
    keyword: Optional[str] = None
) -> List[Transaction]:
    query = select(Transaction)
    
    if start_date:
        query = query.where(Transaction.date >= start_date)
    if end_date:
        query = query.where(Transaction.date <= end_date)
    if category_id:
        query = query.where(Transaction.category_id == category_id)
    if keyword:
        # Simple simple search in shop, content, description
        query = query.where(
            (Transaction.shop.contains(keyword)) | 
            (Transaction.content.contains(keyword)) | 
            (Transaction.description.contains(keyword))
        )
        
    query = query.order_by(Transaction.date.desc()).offset(skip).limit(limit)
    return session.exec(query).all()

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
