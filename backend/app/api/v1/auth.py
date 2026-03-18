from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import requests
from app.core.config import settings

router = APIRouter()

class GoogleAuthRequest(BaseModel):
    code: str

@router.get("/callback/google/backend")
async def google_callback(request: Request, code: str = Query(...)):
    """
    Google からの OAuth callback を処理する GET エンドポイント
    認可コードを受け取って、トークンを交換し、ユーザー情報を取得する
    """
    redirect_uri = settings.REDIRECT_URI
    if not redirect_uri:
        base_url = str(request.base_url).rstrip('/')
        if "run.app" in base_url and base_url.startswith("http://"):
            base_url = base_url.replace("http://", "https://")
        redirect_uri = f"{base_url}/api/auth/callback/google"
    
    print(f"DEBUG: google_callback redirect_uri={redirect_uri}")
    
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    
    token_res = requests.post(token_url, data=token_data)
    if not token_res.ok:
        error_detail = token_res.json() if token_res.text else "Unknown error"
        print(f"DEBUG: Token exchange failed: {error_detail}")
        raise HTTPException(status_code=400, detail=f"Failed to get token from Google: {error_detail}")
    
    access_token = token_res.json().get("access_token")

    # ユーザー情報を取得
    user_info_res = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_info = user_info_res.json()
    email = user_info.get("email")

    # ホワイトリストのチェック
    if not settings.ALLOWED_EMAILS:
        raise HTTPException(status_code=403, detail="Whitelist is empty")
    
    allowed_list = [e.strip().lower() for e in settings.ALLOWED_EMAILS.split(",") if e.strip()]
    if not email or email.lower() not in allowed_list:
        raise HTTPException(status_code=403, detail=f"Access denied: {email} not in whitelist")

    # ログイン成功 → フロント側にリダイレクト
    return RedirectResponse(url="/", status_code=302)

@router.post("/google")
async def google_auth(data: GoogleAuthRequest):
    redirect_uri = settings.REDIRECT_URI or "http://localhost:5173/api/auth/callback/google"
    print(f"DEBUG: google_auth redirect_uri={redirect_uri}")

    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": data.code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    
    token_res = requests.post(token_url, data=token_data)
    if not token_res.ok:
        error_detail = token_res.json() if token_res.text else "Unknown error"
        print(f"DEBUG: Token exchange failed (POST): {error_detail}")
        raise HTTPException(status_code=400, detail=f"Failed to get token from Google: {error_detail}")
    
    access_token = token_res.json().get("access_token")

    user_info_res = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_info = user_info_res.json()
    email = user_info.get("email")

    if not settings.ALLOWED_EMAILS:
        raise HTTPException(status_code=403, detail="Whitelist is empty")
    
    allowed_list = [e.strip().lower() for e in settings.ALLOWED_EMAILS.split(",") if e.strip()]
    if not email or email.lower() not in allowed_list:
        raise HTTPException(status_code=403, detail=f"Access denied: {email} not in whitelist")

    return {
        "status": "success",
        "email": email,
        "name": user_info.get("name"),
        "picture": user_info.get("picture")
    }