from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import requests
from app.core.config import settings

router = APIRouter()

class GoogleAuthRequest(BaseModel):
    code: str

@router.post("/google")
async def google_auth(data: GoogleAuthRequest):
    # 1. Googleへ認可コードを送信し、アクセストークンを取得
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": data.code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": "http://localhost:5173/api/auth/callback/google",
        "grant_type": "authorization_code",
    }
    
    token_res = requests.post(token_url, data=token_data)
    if not token_res.ok:
        raise HTTPException(status_code=400, detail="Failed to get token from Google")
    
    access_token = token_res.json().get("access_token")

    # 2. アクセストークンを使ってユーザー情報を取得
    user_info_res = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_info = user_info_res.json()
    email = user_info.get("email")

    # 3. ホワイトリスト（ALLOWED_EMAILS）のチェック
    if not settings.ALLOWED_EMAILS:
        raise HTTPException(status_code=403, detail="Whitelist is empty")
    
    allowed_list = [e.strip().lower() for e in settings.ALLOWED_EMAILS.split(",") if e.strip()]
    if not email or email.lower() not in allowed_list:
        raise HTTPException(status_code=403, detail=f"Access denied: {email} not in whitelist")

    # 4. ログイン成功！本来はここでJWTを発行しますが、まずはメールを返します
    return {
        "status": "success",
        "email": email,
        "name": user_info.get("name"),
        "picture": user_info.get("picture")
    }