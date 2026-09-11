"""Database setup: engine, session factory, and declarative base."""
from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from src.config import get_database_url
import streamlit as st


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# Engine: manages the actual connection pool to PostgreSQL
@st.cache_resource
def _get_engine():
    """Create the SQLAlchemy engine once per Streamlit session."""
    return create_engine(
        get_database_url(),
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
    )


engine = _get_engine()

# Session factory: creates new sessions on demand
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session and ensure it's closed afterwards.

    Usage:
        with next(get_session()) as session:
            ...

    Or with FastAPI-style dependency injection:
        def endpoint(session: Session = Depends(get_session)):
            ...
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """Create all tables in the database.

    Only used for development. In production, use Alembic migrations.
    """
    # Import models so Base.metadata knows about them
    from src.models import Task, User  # noqa: F401

    Base.metadata.create_all(bind=engine)