from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(title=settings.PROJECT_NAME)

# 1. CORS設定（フロントエンドからの通信を許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://my-kakeibo-frontend.vercel.app",
        "https://my-kakeibo-frontend-git-main-shishidos-projects-49902237.vercel.app",
        "https://my-kakeibo-frontend-git-pdf-import-shishidos-projects-49902237.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. ルーターの登録
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
def on_startup():
    # クラウド(Turso)使用時は、ここで SQLModel.metadata.create_all(engine) を
    # 実行してはいけません（偽Engineのためエラーになります）。
    # テーブル作成は turso shell 等で事前に行っておく運用にします。
    print(f"🚀 {settings.PROJECT_NAME} backend started successfully!")

@app.get("/")
def read_root():
    return {"message": "Welcome to My Kakeibo API! Cloud bypass mode active."}