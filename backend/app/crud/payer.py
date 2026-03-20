from typing import List, Optional

from app.db.session import DatabaseSession
from app.models.payer import Payer
from app.schemas.payer import PayerCreate, PayerUpdate


def _row_to_payer(row: dict | None) -> Optional[Payer]:
    return Payer.model_validate(row) if row else None


def get_payer(session: DatabaseSession, payer_id: int) -> Optional[Payer]:
    row = session.fetch_one(
        f"SELECT id, name, is_active FROM m_payer WHERE id = {payer_id}"
    )
    return _row_to_payer(row)


def get_payers(session: DatabaseSession, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Payer]:
    where_clause = 'WHERE is_active = 1' if active_only else ''
    rows = session.fetch_all(
        f"SELECT id, name, is_active FROM m_payer {where_clause} ORDER BY id LIMIT {limit} OFFSET {skip}"
    )
    return [Payer.model_validate(row) for row in rows]


def create_payer(session: DatabaseSession, payer_in: PayerCreate) -> Payer:
    payer_id = session.insert(
        'm_payer',
        {
            'name': payer_in.name,
            'is_active': True,
        },
    )
    return get_payer(session, int(payer_id))


def update_payer(session: DatabaseSession, payer_id: int, payer_in: PayerUpdate) -> Optional[Payer]:
    existing = get_payer(session, payer_id)
    if not existing:
        return None

    updates = payer_in.model_dump(exclude_unset=True)
    session.update('m_payer', payer_id, updates)
    return get_payer(session, payer_id)


def deactivate_payer(session: DatabaseSession, payer_id: int) -> Optional[Payer]:
    existing = get_payer(session, payer_id)
    if not existing:
        return None

    session.update('m_payer', payer_id, {'is_active': False})
    return get_payer(session, payer_id)
