import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models import User
from app.auth import hash_password, create_access_token

# In-memory SQLite, isolated from the real Postgres database the app
# connects to in app/database.py. StaticPool keeps a single connection alive
# for the whole test session so the in-memory DB isn't dropped between uses.
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def _sqlite_regexp_replace(text, pattern, replacement, flags):
    # /alerts/check-plate normalizes plates with Postgres' 4-arg
    # regexp_replace(), which SQLite has no equivalent for. Registered as a
    # connection-level function so the real production query runs unchanged
    # against the in-memory test database.
    if text is None:
        return None
    py_flags = re.IGNORECASE if flags and "i" in flags else 0
    return re.sub(pattern, replacement, text, flags=py_flags)


@event.listens_for(engine, "connect")
def _configure_sqlite_connection(dbapi_connection, connection_record):
    # SQLite ignores FK constraints (incl. our ON DELETE CASCADE) unless this
    # pragma is set per-connection.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    dbapi_connection.create_function("regexp_replace", 4, _sqlite_regexp_replace)


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
def fresh_schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def make_user(db_session):
    def _make(role="reportee", email=None, badge=None, national_id="123456/10/1", active=True):
        email = email or f"{role}.{db_session.query(User).count()}@test.local"
        user = User(
            first_name="Test", last_name=role.capitalize(), email=email,
            phone="+260971234567", password_hash=hash_password("Password123"),
            role=role, national_id=national_id, badge_number=badge, is_active=active,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    return _make


@pytest.fixture
def auth_headers():
    def _headers(user):
        token = create_access_token(user.id, user.role)
        return {"Authorization": f"Bearer {token}"}
    return _headers
