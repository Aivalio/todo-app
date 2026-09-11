"""Shared pytest fixtures for the To-Do App test suite."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base
from src.models import User, Task  # noqa: F401  (registers models with Base)
from src.services.auth_service import register_user


@pytest.fixture
def engine():
    """In-memory SQLite engine, isolated per test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def session(engine):
    """SQLAlchemy session bound to the in-memory test DB."""
    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    s = TestSession()
    try:
        yield s
    finally:
        s.close()


@pytest.fixture
def sample_user(session):
    """A registered user for use in tests."""
    return register_user(session, "alice", "alice@example.com", "secret123")


@pytest.fixture
def second_user(session):
    """A second user, for cross-user isolation tests."""
    return register_user(session, "bob", "bob@example.com", "secret456")