from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "My Kakeibo API"
    
    # Turso用 (Vercel環境では環境変数から読み込む)
    DATABASE_URL: str
    TURSO_TOKEN: str | None = None  # Turso接続用のトークン
    
    @field_validator("DATABASE_URL", "TURSO_TOKEN", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip().strip('"').strip("'")
        return v

    # Auth.js / Google OAuth
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    ALLOWED_EMAILS: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" # 環境変数に余計な値があってもエラーにしない
    )

settings = Settings()
