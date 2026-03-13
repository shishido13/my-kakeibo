from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from datetime import date

from app.db.session import get_db
from app.services import transaction_service

router = APIRouter()

@router.get("/summary/monthly")
def get_monthly_summary(
    year: int = Query(default=date.today().year, description="Year to summarize"),
    month: int = Query(default=date.today().month, description="Month to summarize"),
    db: Session = Depends(get_db)
):
    """
    指定された年月のサマリー情報（総支出、カテゴリ別など）を取得するエンドポイント
    """
    return transaction_service.get_monthly_summary(db, year, month)
