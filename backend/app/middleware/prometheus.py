import time
import logging
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

REQUEST_COUNT = Counter(
    "cognora_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "cognora_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
)

ACTIVE_REQUESTS = Gauge(
    "cognora_active_requests",
    "Number of active HTTP requests",
)

DB_QUERY_COUNT = Counter(
    "cognora_db_queries_total",
    "Total database queries",
    ["operation"],
)

AI_REQUEST_COUNT = Counter(
    "cognora_ai_requests_total",
    "Total AI API requests",
    ["model", "status"],
)

CACHE_HITS = Counter(
    "cognora_cache_hits_total",
    "Total cache hits/misses",
    ["result"],
)

REDIS_OPERATIONS = Counter(
    "cognora_redis_operations_total",
    "Total Redis operations",
    ["operation", "status"],
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/metrics":
            return Response(
                content=generate_latest(),
                media_type=CONTENT_TYPE_LATEST,
            )

        path = request.url.path
        if path.startswith("/api/"):
            path = self._normalize_path(path)
        method = request.method

        ACTIVE_REQUESTS.inc()
        start_time = time.time()

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            REQUEST_COUNT.labels(
                method=method,
                endpoint=path,
                status_code=response.status_code,
            ).inc()

            REQUEST_LATENCY.labels(
                method=method,
                endpoint=path,
            ).observe(duration)

            return response
        except Exception as exc:
            duration = time.time() - start_time
            REQUEST_COUNT.labels(
                method=method,
                endpoint=path,
                status_code=500,
            ).inc()
            REQUEST_LATENCY.labels(
                method=method,
                endpoint=path,
            ).observe(duration)
            raise
        finally:
            ACTIVE_REQUESTS.dec()

    def _normalize_path(self, path: str) -> str:
        parts = path.strip("/").split("/")
        normalized = []
        for part in parts:
            if part.isdigit() or (
                len(part) > 8 and part[0] in ("a", "b", "c", "d", "e", "f") and "-" in part
            ):
                normalized.append("{id}")
            else:
                normalized.append(part)
        return "/" + "/".join(normalized)
