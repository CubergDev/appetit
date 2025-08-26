from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


def _build_engine():
    url = settings.DATABASE_URL
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(
        url,
        echo=(settings.APP_ENV == "dev"),
        pool_pre_ping=True,
        future=True,
        connect_args=connect_args,
    )


engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


# FastAPI dependency
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def session_scope() -> Iterator["Session"]:
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db() -> Iterator["Session"]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()