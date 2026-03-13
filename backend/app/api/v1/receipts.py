from fastapi import APIRouter, UploadFile, File, Form
from typing import Dict, Any

from app.services import ai_service

router = APIRouter()

@router.post("/analyze")
async def analyze_receipt(
    file: UploadFile = File(...),
):
    """
    アップロードされたレシート画像をAIに解析させ、結果を返すエンドポイント
    """
    
    # 将来的には file.file.read() などで画像データを取得し、AIサービスへ渡す
    content = await file.read()
    
    # ダミーの処理結果を返す（現在はモック）
    result = await ai_service.analyze_receipt_mock(content, file.filename)
    return result
