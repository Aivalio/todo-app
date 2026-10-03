"""Database setup: engine, session factory, and declarative base."""
from collections.abc import Generator

import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.config import get_database_url


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


@st.cache_resource
def _get_engine():
    """Create the SQLAlchemy engine once per Streamlit session."""
    return create_engine(
        get_database_url(),
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
    )


def get_engine():
    """Return the engine, creating it lazily on first call."""
    return _get_engine()


def get_session() -> Generator[Session, None, None]:
    """Yield a database session and ensure it's closed afterwards."""
    SessionLocal = sessionmaker(
        bind=get_engine(),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """Create all tables in the database (dev only)."""
    from src.models import Task, User  # noqa: F401

    Base.metadata.create_all(bind=get_engine())