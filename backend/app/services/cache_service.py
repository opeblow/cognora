import json
import hashlib
from typing import Optional, Any
import redis.asyncio as aioredis
from app.core.config import settings

redis_client = None


def get_redis():
    global redis_client
    if redis_client is None:
        try:
            redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
        except Exception:
            redis_client = None
    return redis_client


def make_cache_key(prefix: str, *args, **kwargs) -> str:
    key = f"{prefix}:{':'.join(str(a) for a in args)}"
    if kwargs:
        key += f":{hashlib.md5(json.dumps(kwargs, sort_keys=True).encode()).hexdigest()}"
    return key


async def get_cached(key: str) -> Optional[str]:
    client = get_redis()
    if not client:
        return None
    try:
        return await client.get(key)
    except Exception:
        return None


async def set_cached(key: str, value: Any, ttl: int = 300):
    client = get_redis()
    if not client:
        return
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await client.setex(key, ttl, value)
    except Exception:
        pass


async def invalidate_cache(pattern: str):
    client = get_redis()
    if not client:
        return
    try:
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
    except Exception:
        pass


def cached(ttl: int = 300):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache_key = make_cache_key(func.__name__, *args, **kwargs)
            cached_value = await get_cached(cache_key)
            if cached_value is not None:
                try:
                    return json.loads(cached_value)
                except (json.JSONDecodeError, TypeError):
                    return cached_value

            result = await func(*args, **kwargs)
            await set_cached(cache_key, result, ttl)
            return result
        return wrapper
    return decorator
