import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///./test.db")
os.environ.setdefault("JWT_SECRET", "test-secret")

from app.main import create_app  # noqa: E402
from app.infra.db.base import init_db, SessionLocal  # noqa: E402
from app.infra.db import models  # noqa: E402
from sqlalchemy import text  # noqa: E402


@pytest.fixture(autouse=True)
def setup_db():
    # Recreate tables cleanly for each test session
    init_db()
    yield
    # Cleanup between tests
    with SessionLocal() as s:
        s.execute(text("DELETE FROM audit_events"))
        s.execute(text("DELETE FROM daily_summaries"))
        s.execute(text("DELETE FROM responses"))
        s.execute(text("DELETE FROM collections"))
        s.execute(text("DELETE FROM ai_integrations"))
        s.execute(text("DELETE FROM teams_integrations"))
        s.execute(text("DELETE FROM users"))
        s.execute(text("DELETE FROM teams"))
        s.execute(text("DELETE FROM organizations"))
        s.commit()


@pytest.fixture()
def db() -> Session:
    with SessionLocal() as s:
        yield s


@pytest.fixture()
def client() -> TestClient:
    app = create_app()
    return TestClient(app)

