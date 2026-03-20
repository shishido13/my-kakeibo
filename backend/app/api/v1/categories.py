from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.db.session import get_session
from app.crud import category as crud_category
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.db.session import DatabaseSession

router = APIRouter()

@router.get("/", response_model=List[CategoryRead])
def read_categories(skip: int = 0, limit: int = 100, active_only: bool = True, session: DatabaseSession = Depends(get_session)):
    return crud_category.get_categories(session, skip=skip, limit=limit, active_only=active_only)

@router.get("/{category_id}", response_model=CategoryRead)
def read_category(category_id: int, session: DatabaseSession = Depends(get_session)):
    db_category = crud_category.get_category(session, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.post("/", response_model=CategoryRead)
def create_category(category_in: CategoryCreate, session: DatabaseSession = Depends(get_session)):
    return crud_category.create_category(session=session, category_in=category_in)

@router.put("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, category_in: CategoryUpdate, session: DatabaseSession = Depends(get_session)):
    updated = crud_category.update_category(session=session, category_id=category_id, category_in=category_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated

@router.put("/{category_id}/deactivate", response_model=CategoryRead)
def deactivate_category(category_id: int, session: DatabaseSession = Depends(get_session)):
    updated = crud_category.deactivate_category(session=session, category_id=category_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated
