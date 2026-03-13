from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_session
from app.crud import payer as crud_payer
from app.schemas.payer import PayerCreate, PayerRead, PayerUpdate

router = APIRouter()

@router.get("/", response_model=List[PayerRead])
def read_payers(skip: int = 0, limit: int = 100, active_only: bool = True, session: Session = Depends(get_session)):
    return crud_payer.get_payers(session, skip=skip, limit=limit, active_only=active_only)

@router.get("/{payer_id}", response_model=PayerRead)
def read_payer(payer_id: int, session: Session = Depends(get_session)):
    db_payer = crud_payer.get_payer(session, payer_id=payer_id)
    if not db_payer:
        raise HTTPException(status_code=404, detail="Payer not found")
    return db_payer

@router.post("/", response_model=PayerRead)
def create_payer(payer_in: PayerCreate, session: Session = Depends(get_session)):
    return crud_payer.create_payer(session=session, payer_in=payer_in)

@router.put("/{payer_id}", response_model=PayerRead)
def update_payer(payer_id: int, payer_in: PayerUpdate, session: Session = Depends(get_session)):
    db_payer = crud_payer.get_payer(session, payer_id=payer_id)
    if not db_payer:
        raise HTTPException(status_code=404, detail="Payer not found")
    return crud_payer.update_payer(session=session, db_payer=db_payer, payer_in=payer_in)

@router.put("/{payer_id}/deactivate", response_model=PayerRead)
def deactivate_payer(payer_id: int, session: Session = Depends(get_session)):
    db_payer = crud_payer.get_payer(session, payer_id=payer_id)
    if not db_payer:
        raise HTTPException(status_code=404, detail="Payer not found")
    return crud_payer.deactivate_payer(session=session, db_payer=db_payer)
