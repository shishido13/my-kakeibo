from sqlmodel import create_engine, Session
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL, 
    echo=True, 
    connect_args={"check_same_thread": False} # Required for SQLite
)

def get_db():
    with Session(engine) as session:
        yield session

# Alias for backward compatibility
get_session = get_db
