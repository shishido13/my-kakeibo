from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router as api
from app.api.v1.auth import router as auth
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title=settings.PROJECT_NAME)

# 1. CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. ルーターの登録
app.include_router(api, prefix="/api/v1")
app.include_router(auth, prefix="/api/auth")

@app.on_event("startup")
def on_startup():
    print(f"🚀 {settings.PROJECT_NAME} backend started successfully!")

# 3. 静的ファイル（フロントエンド）の配信設定
static_dir = os.path.join(os.path.dirname(__file__), "static")

if os.path.exists(static_dir):
    # assets (JS/CSS) の配信
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="static")

    # 全てのリクエストを SPA として index.html に誘導する
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        is_api_endpoint = full_path.startswith("api/v1") or full_path == "api/auth/google"
        
        if is_api_endpoint:
            return None 
        file_path = os.path.join(static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        
        return FileResponse(os.path.join(static_dir, "index.html"))

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(static_dir, "index.html"))
else:
    @app.get("/")
    def read_root():
        return {"message": "Welcome to My Kakeibo API! Static files not found."}