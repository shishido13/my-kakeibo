from typing import List, Optional
from sqlmodel import Session, select
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

def get_category(session: Session, category_id: int) -> Optional[Category]:
    return session.get(Category, category_id)

def get_categories(session: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Category]:
    query = select(Category)
    if active_only:
        query = query.where(Category.is_active == True)
    query = query.offset(skip).limit(limit)
    return session.exec(query).all()

def create_category(session: Session, category_in: CategoryCreate) -> Category:
    db_category = Category.model_validate(category_in)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

def update_category(session: Session, db_category: Category, category_in: CategoryUpdate) -> Category:
    category_data = category_in.model_dump(exclude_unset=True)
    for key, value in category_data.items():
        setattr(db_category, key, value)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

def deactivate_category(session: Session, db_category: Category) -> Category:
    db_category.is_active = False
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category
