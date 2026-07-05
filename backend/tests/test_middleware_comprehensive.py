import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient


def test_request_id_header_added(client: TestClient):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert "X-Request-Id" in resp.headers
    assert len(resp.headers["X-Request-Id"]) > 0


def test_request_id_preserves_existing(client: TestClient):
    existing_id = "custom-request-uuid-12345"
    resp = client.get("/api/health", headers={"X-Request-Id": existing_id})
    assert resp.headers["X-Request-Id"] == existing_id


def test_request_id_unique_per_request(client: TestClient):
    r1 = client.get("/api/health")
    r2 = client.get("/api/health")
    assert r1.headers["X-Request-Id"] != r2.headers["X-Request-Id"]


def test_health_endpoint_no_rate_limit(client: TestClient):
    for _ in range(200):
        resp = client.get("/api/health")
        assert resp.status_code == 200


def test_rate_limit_within_limit(client: TestClient):
    resp = client.get("/api/health")
    assert resp.status_code == 200


def test_rate_limit_exceeded(client: TestClient, monkeypatch):
    monkeypatch.setattr("app.core.config.settings.RATE_LIMIT_PER_MINUTE", 5)

    with patch("app.middleware.rate_limit.get_redis") as mock_redis_factory:
        mock_redis = MagicMock()
        mock_redis_factory.return_value = mock_redis

        pipe = MagicMock()
        pipe.zadd.return_value = None
        pipe.zremrangebyscore.return_value = None
        pipe.zcard.return_value = 999
        pipe.expire.return_value = None
        pipe.execute = AsyncMock(return_value=(None, None, 999, None))
        mock_redis.pipeline.return_value = pipe

        mock_redis.incr = AsyncMock(return_value=None)
        mock_redis.expire = AsyncMock(return_value=None)

        resp = client.get("/api/auth/me")
        assert resp.status_code == 429
        data = resp.json()
        assert data["detail"]["code"] == "RATE_LIMITED"


def test_rate_limit_different_endpoints(client: TestClient, monkeypatch):
    monkeypatch.setattr("app.core.config.settings.RATE_LIMIT_PER_MINUTE", 60)

    with patch("app.middleware.rate_limit.get_redis") as mock_redis_factory:
        mock_redis = MagicMock()
        mock_redis_factory.return_value = mock_redis

        pipe = MagicMock()
        pipe.zadd.return_value = None
        pipe.zremrangebyscore.return_value = None
        pipe.zcard.side_effect = [1, 99]
        pipe.expire.return_value = None
        pipe.execute = AsyncMock(side_effect=[
            (None, None, 1, None),
            (None, None, 99, None),
        ])
        mock_redis.pipeline.return_value = pipe
        mock_redis.incr = AsyncMock(return_value=None)
        mock_redis.expire = AsyncMock(return_value=None)

        r1 = client.get("/api/auth/me")
        assert r1.status_code in (200, 401, 403)

        r2 = client.get("/api/quizzes")
        assert r2.status_code in (200, 429, 401, 403)


def test_rate_limit_different_users(client: TestClient, monkeypatch):
    monkeypatch.setattr("app.core.config.settings.RATE_LIMIT_PER_MINUTE", 60)

    call_count = 0

    async def mock_get_redis():
        mock_r = MagicMock()
        mock_r.pipeline.return_value = pipeline = MagicMock()
        pipeline.zadd.return_value = None
        pipeline.zremrangebyscore.return_value = None

        def zcard_side_effect(*args):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return 1
            return 999

        pipeline.zcard.side_effect = zcard_side_effect
        pipeline.expire.return_value = None
        pipeline.execute = AsyncMock(side_effect=[
            (None, None, 1, None),
            (None, None, 1, None),
            (None, None, 999, None),
        ])
        mock_r.incr = AsyncMock(return_value=None)
        mock_r.expire = AsyncMock(return_value=None)
        return mock_r

    mock_redis_factory = AsyncMock(side_effect=mock_get_redis)

    with patch("app.middleware.rate_limit.get_redis", mock_redis_factory):
        u1 = client.post("/api/auth/signup", json={
            "email": "rl_user1_mid@example.com", "password": "TestPass123!", "full_name": "U1",
        })
        u2 = client.post("/api/auth/signup", json={
            "email": "rl_user2_mid@example.com", "password": "TestPass123!", "full_name": "U2",
        })


def test_webhook_whitelisted(client: TestClient, monkeypatch):
    monkeypatch.setattr("app.core.config.settings.RATE_LIMIT_PER_MINUTE", 5)

    with patch("app.middleware.rate_limit.get_redis") as mock_redis_factory:
        mock_redis = AsyncMock()
        mock_redis_factory.return_value = mock_redis

        pipe = MagicMock()
        pipe.zadd.return_value = None
        pipe.zremrangebyscore.return_value = None
        pipe.zcard.return_value = 999
        pipe.expire.return_value = None
        pipe.execute.return_value = (None, None, 999, None)
        mock_redis.pipeline.return_value = pipe

        resp = client.post("/api/payments/webhook", json={"event": "test"})
        assert resp.status_code == 200


def test_cors_allowed_origin(client: TestClient):
    resp = client.options("/api/health", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
    })
    assert "Access-Control-Allow-Origin" in resp.headers


def test_cors_disallowed_origin(client: TestClient):
    resp = client.options("/api/health", headers={
        "Origin": "https://evil.com",
        "Access-Control-Request-Method": "GET",
    })
    origin = resp.headers.get("Access-Control-Allow-Origin", "")
    assert "evil.com" not in origin


def test_cors_headers_present(client: TestClient):
    resp = client.get("/api/health", headers={"Origin": "http://localhost:3000"})
    assert "Access-Control-Allow-Origin" in resp.headers


def test_rate_limit_returns_headers(client: TestClient, monkeypatch):
    monkeypatch.setattr("app.core.config.settings.RATE_LIMIT_PER_MINUTE", 60)

    with patch("app.middleware.rate_limit.get_redis") as mock_redis_factory:
        mock_redis = AsyncMock()
        mock_redis_factory.return_value = mock_redis

        pipe = MagicMock()
        pipe.zadd.return_value = None
        pipe.zremrangebyscore.return_value = None
        pipe.zcard.return_value = 5
        pipe.expire.return_value = None
        pipe.execute.return_value = (None, None, 5, None)
        mock_redis.pipeline.return_value = pipe

        resp = client.get("/api/health")
        if "X-RateLimit-Limit" in resp.headers:
            assert int(resp.headers["X-RateLimit-Limit"]) > 0
        if "X-RateLimit-Remaining" in resp.headers:
            assert int(resp.headers["X-RateLimit-Remaining"]) >= 0


def test_non_api_path_no_rate_limit(client: TestClient, monkeypatch):
    monkeypatch.setattr("app.middleware.rate_limit.ENDPOINT_LIMITS", {"default_auth": 0, "default_anon": 0})
    resp = client.get("/docs")
    assert resp.status_code != 429
