import asyncio
import logging
from contextlib import asynccontextmanager
from urllib.parse import urlparse
from sqlalchemy import text
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import settings
from app.core.errors import AppError, app_error_handler, unhandled_error_handler
from app.core.logging import setup_logging
from app.middleware.cors import setup_cors
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.prometheus import PrometheusMiddleware
from app.core.sentry import init_sentry
from app.routes.api import auth, subjects, ai, quizzes, exams, dashboard, credits, lessons, textbook, study_planner, analytics as analytics_router, settings as settings_router, upload, audio, live, gamification, lobby, flashcard, payments, issues, content, study_groups, past_questions
from app.database.base import engine
from app.database.redis import get_redis, close_redis

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging("DEBUG" if settings.DEBUG else "INFO")
    redis_ok = False
    db_ok = False
    try:
        client = await get_redis()
        await client.ping()
        redis_ok = True
    except Exception as e:
        logger.warning(f"Redis connection failed on startup: {e}")
    try:
        def _check_db():
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        await asyncio.to_thread(_check_db)
        db_ok = True
    except Exception as e:
        logger.warning(f"Database connection failed on startup: {e}")
    logger.info(f"Startup checks — DB: {'OK' if db_ok else 'FAIL'}, Redis: {'OK' if redis_ok else 'FAIL'}")
    yield
    try:
        await close_redis()
        logger.info("Redis connections closed on shutdown")
    except Exception as e:
        logger.warning(f"Error closing Redis connections on shutdown: {e}")


def create_app() -> FastAPI:
    init_sentry()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    setup_cors(app)
    app.add_middleware(PrometheusMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(RateLimitMiddleware)

    allowed_hosts = ["localhost", "127.0.0.1", "testserver"]
    if settings.APP_URL:
        try:
            host = urlparse(settings.APP_URL).hostname
            if host and host not in allowed_hosts:
                allowed_hosts.append(host)
        except Exception:
            pass
    if settings.DEBUG:
        allowed_hosts = ["*"]

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts,
    )

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)

    routers = [
        auth.router, subjects.router, ai.router, quizzes.router, exams.router,
        dashboard.router, credits.router, lessons.router, textbook.router,
        study_planner.router, analytics_router.router, settings_router.router,
        upload.router, audio.router, live.router, gamification.router,
        lobby.router, flashcard.router, payments.router, issues.router,
        content.router, study_groups.router, past_questions.router,
    ]
    for router in routers:
        app.include_router(router, prefix="/api")

    @app.get("/api/health")
    async def health_check():
        from fastapi.responses import JSONResponse
        deps = {"status": "ok", "version": settings.APP_VERSION}
        status_code = 200
        try:
            def _check_db():
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
            await asyncio.to_thread(_check_db)
            deps["database"] = "connected"
        except Exception as e:
            logger.warning("Health database check failed: %s", e)
            deps["database"] = "unavailable"
            deps["status"] = "degraded"
            status_code = 503
        try:
            client = await get_redis()
            await client.ping()
            deps["redis"] = "connected"
        except Exception as e:
            logger.warning("Health Redis check failed: %s", e)
            deps["redis"] = "unavailable"
            deps["status"] = "degraded"
            status_code = 503
        try:
            from app.utils.celery_safe import _broker_available as celery_ok
            deps["celery"] = "available" if celery_ok else "broker unavailable"
        except Exception:
            deps["celery"] = "unavailable"
        return JSONResponse(content=deps, status_code=status_code)

    return app


app = create_app()
