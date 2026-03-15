from fastapi import APIRouter, UploadFile, File, Depends
from sqlmodel import Session
from typing import List, Dict, Any

from app.services import ai_service
from app.db.session import get_db
from app.schemas.transaction import TransactionCreate

router = APIRouter()

@router.post("/analyze", response_model=List[TransactionCreate])
async def analyze_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    アップロードされたPDFレシートをGemini AIで解析し、
    トランザクション（候補）のリストを返す。
    """
    content = await file.read()
    
    transactions = await ai_service.analyze_pdf_receipt(content, file.filename, db)
    return transactions
