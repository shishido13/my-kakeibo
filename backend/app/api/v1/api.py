from fastapi import APIRouter
from app.api.v1 import transactions, categories, payers, analytics, receipts

api_router = APIRouter()
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(payers.router, prefix="/payers", tags=["payers"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(receipts.router, prefix="/receipts", tags=["receipts"])
