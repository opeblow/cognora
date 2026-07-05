import logging
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)


class NullRedis:
    """Graceful fallback when Redis is unavailable. All operations are no-ops."""

    async def ping(self):
        return True

    async def get(self, key):
        return None

    async def setex(self, key, time, value):
        pass

    async def delete(self, *keys):
        pass

    async def keys(self, pattern):
        return []

    async def incr(self, key):
        return 1

    async def expire(self, key, time):
        pass

    async def zadd(self, key, mapping):
        return 0

    async def zremrangebyscore(self, key, min, max):
        return 0

    async def zcard(self, key):
        return 0

    async def close(self):
        pass

    def pipeline(self):
        return NullPipeline()


class NullPipeline:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    def zadd(self, key, mapping):
        return self

    def zremrangebyscore(self, key, min, max):
        return self

    def zcard(self, key):
        return self

    def expire(self, key, time):
        return self

    async def execute(self):
        return [0, 0, 0, True]


_client = None


async def get_redis():
    global _client
    if _client is not None:
        return _client
    if not settings.REDIS_URL:
        logger.info("REDIS_URL not set, using in-memory fallback")
        _client = NullRedis()
        return _client
    try:
        c = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await c.ping()
        _client = c
        logger.info("Connected to Redis")
    except Exception as e:
        logger.warning(f"Redis unavailable ({e}), using in-memory fallback")
        _client = NullRedis()
    return _client


async def close_redis():
    global _client
    if _client and not isinstance(_client, NullRedis):
        await _client.close()
    _client = None
