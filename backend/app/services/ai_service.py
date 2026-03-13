from typing import Dict, Any
import asyncio

async def analyze_receipt_mock(image_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    モックのレシート解析処理
    本来はここでGeminiなどの画像認識AI APIを呼び出す
    """
    # 通信の遅延をシミュレート
    await asyncio.sleep(1.5)
    
    return {
        "status": "success",
        "message": f"{filename} の解析が完了しました（モック）",
        "data": {
            "shop": "スーパー◯◯",
            "date": "2023-11-20",
            "total_amount": 2580,
            "items": [
                {"name": "キャベツ", "price": 150},
                {"name": "豚肉", "price": 500},
                {"name": "牛乳", "price": 200}
            ],
            "suggested_category": "食費" 
        }
    }
