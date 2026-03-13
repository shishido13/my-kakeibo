from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "My Kakeibo API"
    DATABASE_URL: str = "sqlite:///./db_data/kakeibo.db" # Default for local/docker

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
