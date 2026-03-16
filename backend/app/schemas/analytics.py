from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class CategorySummary(BaseModel):
    category_id: int
    category_name: str
    amount: int

class PayerSummary(BaseModel):
    payer: str
    amount: int

class AnalyticsSummary(BaseModel):
    total_amount: int
    categories: List[CategorySummary]
    payers: List[PayerSummary]
    period_label: str  # e.g., "2024-03"
    previous_total_amount: Optional[int] = None
    comparison_percentage: Optional[float] = None

class TrendPoint(BaseModel):
    label: str  # e.g., "2024-03-01" or "2024-W1"
    amount: int

class AnalyticsTrend(BaseModel):
    period_type: str  # "yearly", "monthly", "weekly"
    data: List[TrendPoint]
