from typing import List, Optional
from sqlmodel import Session, select
from app.models.payer import Payer
from app.schemas.payer import PayerCreate, PayerUpdate

def get_payer(session: Session, payer_id: int) -> Optional[Payer]:
    return session.get(Payer, payer_id)

def get_payers(session: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Payer]:
    query = select(Payer)
    if active_only:
        query = query.where(Payer.is_active == True)
    query = query.offset(skip).limit(limit)
    return session.exec(query).all()

def create_payer(session: Session, payer_in: PayerCreate) -> Payer:
    db_payer = Payer.model_validate(payer_in)
    session.add(db_payer)
    session.commit()
    session.refresh(db_payer)
    return db_payer

def update_payer(session: Session, db_payer: Payer, payer_in: PayerUpdate) -> Payer:
    payer_data = payer_in.model_dump(exclude_unset=True)
    for key, value in payer_data.items():
        setattr(db_payer, key, value)
    session.add(db_payer)
    session.commit()
    session.refresh(db_payer)
    return db_payer

def deactivate_payer(session: Session, db_payer: Payer) -> Payer:
    db_payer.is_active = False
    session.add(db_payer)
    session.commit()
    session.refresh(db_payer)
    return db_payer
