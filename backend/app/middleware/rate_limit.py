from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.database.redis import get_redis, NullRedis
import time
import asyncio


ENDPOINT_LIMITS: dict[str, int] = {
    "/api/auth/": 10,
    "/api/ai/generate": 5,
    "/api/payments/": 30,
    "/api/live/ws": 60,
    "/api/quizzes/": 60,
    "/api/exams/": 60,
    "default_anon": 30,
    "default_auth": 100,
}

_in_memory_store: dict[str, list[float]] = {}
_in_memory_lock = asyncio.Lock()
_last_cleanup = time.time()


async def _check_rate_limit_redis(key: str, max_r: int) -> tuple[bool, int]:
    redis = await get_redis()
    if isinstance(redis, NullRedis):
        raise RuntimeError("Redis rate limiter unavailable")
    now = int(time.time() * 1000)
    window = 60_000

    pipe = redis.pipeline()
    pipe.zadd(key, {str(now): now})
    pipe.zremrangebyscore(key, 0, now - window)
    pipe.zcard(key)
    pipe.expire(key, 120)
    _, _, count, _ = await pipe.execute()

    return count > max_r, count


async def _check_rate_limit_memory(key: str, max_r: int) -> tuple[bool, int]:
    global _last_cleanup
    now = time.time()
    window = 60.0

    async with _in_memory_lock:
        if now - _last_cleanup > 300:
            expired_keys = [k for k, v in _in_memory_store.items() if all(t < now - window for t in v)]
            for k in expired_keys:
                del _in_memory_store[k]
            _last_cleanup = now

        timestamps = _in_memory_store.get(key, [])
        timestamps = [t for t in timestamps if t > now - window]
        timestamps.append(now)
        _in_memory_store[key] = timestamps

    return len(timestamps) > max_r, len(timestamps)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if not path.startswith("/api/") or path == "/api/health":
            return await call_next(request)

        if path in ("/api/payments/webhook", "/api/email/webhook"):
            return await call_next(request)

        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                try:
                    from app.core.security import decode_token
                    payload = decode_token(auth_header[7:])
                    if payload and payload.get("sub"):
                        user_id = payload["sub"]
                        request.state.user_id = user_id
                except Exception:
                    pass

        ip = request.client.host if request.client else "unknown"

        max_r = ENDPOINT_LIMITS["default_auth"] if user_id else ENDPOINT_LIMITS["default_anon"]
        matched_prefix = "default"
        for prefix, limit in ENDPOINT_LIMITS.items():
            if prefix not in ("default_anon", "default_auth") and path.startswith(prefix):
                max_r = limit
                matched_prefix = prefix
                break

        key = f"ratelimit:{user_id or ip}:{matched_prefix}"

        try:
            exceeded, count = await _check_rate_limit_redis(key, max_r)
        except Exception:
            exceeded, count = await _check_rate_limit_memory(key, max_r)

        if exceeded:
            retry_after = 60
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": {
                        "code": "RATE_LIMITED",
                        "message": f"Too many requests. Limit: {max_r}/minute.",
                        "retry_after_seconds": retry_after,
                    }
                },
                headers={"Retry-After": str(retry_after)},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_r)
        response.headers["X-RateLimit-Remaining"] = str(max(0, max_r - count))
        return response
