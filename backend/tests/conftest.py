import pytest
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from app.database.base import Base, get_db
from app.main import app


@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """Prevent all Redis connections during tests."""
    from app.core.config import settings
    settings.REDIS_URL = ""

    mock_pipeline = MagicMock()
    mock_pipeline.zadd.return_value = None
    mock_pipeline.zremrangebyscore.return_value = None
    mock_pipeline.zcard.return_value = 0
    mock_pipeline.expire.return_value = True
    mock_pipeline.execute = AsyncMock(return_value=(None, None, 0, True))

    mock_redis_client = MagicMock()
    mock_redis_client.ping = AsyncMock(return_value=True)
    mock_redis_client.pipeline.return_value = mock_pipeline

    async def mock_get_redis():
        return mock_redis_client

    monkeypatch.setattr("app.middleware.rate_limit.get_redis", mock_get_redis)
    monkeypatch.setattr("app.database.redis.get_redis", mock_get_redis)


@pytest.fixture(autouse=True)
def mock_email(monkeypatch):
    """Prevent real email sending during tests."""
    mock_instance = MagicMock()
    mock_instance.send_email.return_value = True
    mock_instance.send_verification_email.return_value = True
    mock_instance.send_password_reset_email.return_value = True

    mock_class = MagicMock(return_value=mock_instance)
    monkeypatch.setattr("app.utils.email.EmailService", mock_class)
    monkeypatch.setattr("app.services.auth_service.EmailService", mock_class)


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    engine = create_engine(f"sqlite:///{db_path}", echo=False, connect_args={"check_same_thread": False, "timeout": 15})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    engine.dispose()
    if os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except PermissionError:
            pass


@pytest.fixture
def db_session(client):
    """Provide a session to the same database used by the client fixture."""
    db_gen = app.dependency_overrides[get_db]()
    db = next(db_gen)
    try:
        yield db
    finally:
        db_gen.close()
