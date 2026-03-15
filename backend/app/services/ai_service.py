import os
import json
import asyncio
import tempfile
from typing import Dict, Any, List
from google import genai
from sqlmodel import Session
from app.core.config import settings
from app.crud import category, payer

# Using google-genai Client internally

async def analyze_pdf_receipt(file_bytes: bytes, filename: str, db: Session) -> List[Dict[str, Any]]:
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in environment variables.")

    # 1. Fetch reference data
    categories = category.get_categories(db)
    payers = payer.get_payers(db)
    
    cat_map = {c.name: c.id for c in categories}
    payer_names = [p.name for p in payers]
    cat_names = list(cat_map.keys())
    
    default_cat_id = categories[0].id if categories else 1
    default_payer = payer_names[0] if payer_names else "自分"

    # 2. Save bytes to temp file because genai.upload_file needs a path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    def _sync_genai_call() -> str:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        gemini_file = None
        try:
            gemini_file = client.files.upload(file=tmp_path, config={'mime_type': 'application/pdf'})
            
            prompt = f"""
あなたは優秀な経理アシスタントです。添付されたPDF（レシートやクレジットカード明細など）から、**「1商品（1品目）につき1つのJSONオブジェクト」**として情報を抽出し、必ず指定のJSON配列形式で出力してください。

### 抽出ルール:
1.  **商品単位の抽出**: レシートの合計金額ではなく、記載されている個々の商品・サービスごとにデータを作成してください。
2.  **共通情報の補完**: 同一レシート内にある複数の商品については、"date"、"shop"、"payer_name" などの共通情報はすべてのオブジェクトにコピーして含めてください。
3.  **カテゴリ推測**: "category_name" は、レシート全体ではなく「個々の商品内容」に基づいて、以下のリストから最も適切なものを選択してください。

既存カテゴリ: {cat_names}
既存支払者: {payer_names}

### 出力フォーマット:
[
  {{
    "date": "YYYY-MM-DD",
    "amount": <個々の商品の金額（単価×数量、または行の小計）を整数で記入>,
    "shop": "<店舗名>",
    "content": "<具体的な商品名やサービス名>",
    "category_name": "<商品内容にマッチしたカテゴリ名>",
    "payer_name": "<マッチした支払者名、明記なければ俊介>",
    "description": "<必要に応じて、軽減税率の有無や個数などの補足>"
  }}
]

JSON配列のみを出力し、マークダウンブロック（```json など）や解説などの余計な文字列を一切含めないでください。
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[gemini_file, prompt]
            )
            return response.text
        finally:
            if gemini_file:
                client.files.delete(name=gemini_file.name)

    try:
        # Run sync API in thread
        raw_text = await asyncio.to_thread(_sync_genai_call)
        
        # 5. Parse and map results
        text = raw_text.strip()
        if text.startswith("```json"):
            text = text.replace("```json", "", 1)
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
            
        ai_data = json.loads(text.strip())
        
        transactions = []
        for item in ai_data:
            c_name = item.get("category_name", "")
            cat_id = cat_map.get(c_name, default_cat_id)
            
            p_name = item.get("payer_name", default_payer)
            if p_name not in payer_names:
                p_name = default_payer
                
            tx = {
                "date": item.get("date"),
                "amount": item.get("amount", 0),
                "shop": item.get("shop", ""),
                "content": item.get("content", ""),
                "category_id": cat_id,
                "payer": p_name,
                "description": item.get("description", ""),
                "source_type": "ai_pdf"
            }
            transactions.append(tx)
            
        return transactions

    except Exception as e:
        print(f"Error analyzing PDF: {e}")
        return []
        
    finally:
        # Cleanup temp file
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

async def analyze_receipt_mock(image_bytes: bytes, filename: str) -> Dict[str, Any]:
    """モックのレシート解析処理 (互換性用)"""
    await asyncio.sleep(1.5)
    return {
        "status": "success",
        "message": f"{filename} の解析完了（モック）",
        "data": {
            "shop": "スーパー◯◯",
            "date": "2023-11-20",
            "total_amount": 2580,
            "items": [
                {"name": "キャベツ", "price": 150},
                {"name": "豚肉", "price": 500}
            ],
            "suggested_category": "食費" 
        }
    }
