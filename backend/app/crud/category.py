from typing import List, Optional

from app.db.session import DatabaseSession
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def _row_to_category(row: dict | None) -> Optional[Category]:
    return Category.model_validate(row) if row else None


def get_category(session: DatabaseSession, category_id: int) -> Optional[Category]:
    row = session.fetch_one(
        f"SELECT id, name, is_active FROM m_category WHERE id = {category_id}"
    )
    return _row_to_category(row)


def get_categories(session: DatabaseSession, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Category]:
    where_clause = 'WHERE is_active = 1' if active_only else ''
    rows = session.fetch_all(
        f"SELECT id, name, is_active FROM m_category {where_clause} ORDER BY id LIMIT {limit} OFFSET {skip}"
    )
    return [Category.model_validate(row) for row in rows]


def create_category(session: DatabaseSession, category_in: CategoryCreate) -> Category:
    category_id = session.insert(
        'm_category',
        {
            'name': category_in.name,
            'is_active': True,
        },
    )
    return get_category(session, int(category_id))


def update_category(session: DatabaseSession, category_id: int, category_in: CategoryUpdate) -> Optional[Category]:
    existing = get_category(session, category_id)
    if not existing:
        return None

    updates = category_in.model_dump(exclude_unset=True)
    session.update('m_category', category_id, updates)
    return get_category(session, category_id)


def deactivate_category(session: DatabaseSession, category_id: int) -> Optional[Category]:
    existing = get_category(session, category_id)
    if not existing:
        return None

    session.update('m_category', category_id, {'is_active': False})
    return get_category(session, category_id)
