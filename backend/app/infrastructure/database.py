from pathlib import Path

from sqlmodel import Session, create_engine

from app.infrastructure.config import settings

# Resolve DB path relative to the backend/ root, regardless of CWD
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_URL = f"sqlite:///{_BACKEND_DIR / settings.database_path}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

def get_session():
    with Session(engine) as session:
        yield session
