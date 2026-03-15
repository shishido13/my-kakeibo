from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.db.session import get_session
from app.crud import transaction as crud_transaction
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate

router = APIRouter()

@router.get("/", response_model=List[TransactionRead])
def read_transactions(
    skip: int = 0, 
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_ids: List[int] = Query(None),
    payer: Optional[str] = None,
    keyword: Optional[str] = None,
    session: Session = Depends(get_session)
):
    return crud_transaction.get_transactions(
        session, skip=skip, limit=limit, 
        start_date=start_date, end_date=end_date, 
        category_ids=category_ids, payer=payer, keyword=keyword
    )

@router.get("/{transaction_id}", response_model=TransactionRead)
def read_transaction(transaction_id: int, session: Session = Depends(get_session)):
    db_transaction = crud_transaction.get_transaction(session, transaction_id=transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@router.post("/", response_model=TransactionRead)
def create_transaction(transaction_in: TransactionCreate, session: Session = Depends(get_session)):
    return crud_transaction.create_transaction(session=session, transaction_in=transaction_in)

@router.post("/bulk", response_model=List[TransactionRead])
def create_transactions_bulk(transactions_in: List[TransactionCreate], session: Session = Depends(get_session)):
    created = []
    # Using simple loop to create iteratively for now. Bulk inserts can be optimized later
    for tx_in in transactions_in:
        created.append(crud_transaction.create_transaction(session=session, transaction_in=tx_in))
    return created

@router.put("/{transaction_id}", response_model=TransactionRead)
def update_transaction(transaction_id: int, transaction_in: TransactionUpdate, session: Session = Depends(get_session)):
    db_transaction = crud_transaction.get_transaction(session, transaction_id=transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return crud_transaction.update_transaction(session=session, db_transaction=db_transaction, transaction_in=transaction_in)

@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, session: Session = Depends(get_session)):
    db_transaction = crud_transaction.get_transaction(session, transaction_id=transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    crud_transaction.delete_transaction(session=session, db_transaction=db_transaction)
    return {"message": "Transaction deleted successfully"}
