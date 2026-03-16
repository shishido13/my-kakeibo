from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import List, Optional
from datetime import date, timedelta
from app.db.session import get_session
from app import crud
from app.schemas.analytics import AnalyticsSummary, AnalyticsTrend

router = APIRouter()

@router.get("/summary", response_model=AnalyticsSummary)
def read_analytics_summary(
    *,
    session: Session = Depends(get_session),
    start_date: date,
    end_date: date,
    compare: bool = False
):
    prev_start = None
    prev_end = None
    
    if compare:
        # Calculate previous period (same duration)
        duration = (end_date - start_date).days + 1
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end - timedelta(days=duration - 1)

    summary = crud.transaction.get_analytics_summary(
        session=session,
        start_date=start_date,
        end_date=end_date,
        prev_start_date=prev_start,
        prev_end_date=prev_end
    )
    
    # Add period label
    summary["period_label"] = f"{start_date} ~ {end_date}"
    
    return summary

@router.get("/trend", response_model=List[AnalyticsTrend])
def read_analytics_trend(
    *,
    session: Session = Depends(get_session),
    start_date: date,
    end_date: date,
    group_by: str = Query("month", regex="^(day|week|month)$")
):
    trend_data = crud.transaction.get_analytics_trend(
        session=session,
        start_date=start_date,
        end_date=end_date,
        group_by_type=group_by
    )
    
    return [{"period_type": group_by, "data": trend_data}]
