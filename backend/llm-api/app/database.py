from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os

# Local-First: Default to SQLite.
# Cloud-Ready: Can be swapped for "postgresql://..." via env var.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./audit_log.db")

# check_same_thread=False is needed only for SQLite
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency injection for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
