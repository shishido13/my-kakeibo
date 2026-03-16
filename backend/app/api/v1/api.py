from fastapi import APIRouter
from app.api.v1 import transactions, categories, payers, receipts, analytics

api_router = APIRouter()

api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(payers.router, prefix="/payers", tags=["Payers"])
api_router.include_router(receipts.router, prefix="/receipts", tags=["Receipts"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

