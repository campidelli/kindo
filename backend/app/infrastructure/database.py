from sqlmodel import Session, create_engine

from app.infrastructure.config import settings

DATABASE_URL = f"sqlite:///{settings.database_path}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

def get_session():
    with Session(engine) as session:
        yield session
