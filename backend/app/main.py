import logging
from contextlib import asynccontextmanager
from sqlalchemy import text
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import settings
from app.core.errors import AppError, app_error_handler, unhandled_error_handler
from app.middleware.cors import setup_cors
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.routes.api import auth, subjects, ai, quizzes, exams, dashboard, credits, lessons, textbook, study_planner, analytics as analytics_router, settings as settings_router, upload, audio, live, gamification, lobby, flashcard, payments, issues, content
from app.database.base import engine
from app.database.redis import get_redis

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_ok = False
    db_ok = False
    try:
        client = await get_redis()
        await client.ping()
        redis_ok = True
    except Exception as e:
        logger.warning(f"Redis connection failed on startup: {e}")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception as e:
        logger.warning(f"Database connection failed on startup: {e}")
    logger.info(f"Startup checks — DB: {'OK' if db_ok else 'FAIL'}, Redis: {'OK' if redis_ok else 'FAIL'}")
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    setup_cors(app)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(RateLimitMiddleware)

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],
    )

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)

    routers = [
        auth.router, subjects.router, ai.router, quizzes.router, exams.router,
        dashboard.router, credits.router, lessons.router, textbook.router,
        study_planner.router, analytics_router.router, settings_router.router,
        upload.router, audio.router, live.router, gamification.router,
        lobby.router, flashcard.router, payments.router, issues.router,
        content.router,
    ]
    for router in routers:
        app.include_router(router, prefix="/api")

    @app.get("/api/health")
    def health_check():
        deps = {"status": "ok", "version": settings.APP_VERSION}
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            deps["database"] = "connected"
        except Exception as e:
            deps["database"] = f"error: {e}"
            deps["status"] = "degraded"
        try:
            import redis as sync_redis
            r = sync_redis.from_url(settings.REDIS_URL, socket_connect_timeout=3)
            r.ping()
            r.close()
            deps["redis"] = "connected"
        except Exception as e:
            deps["redis"] = f"error: {e}"
            deps["status"] = "degraded"
        return deps

    return app


app = create_app()
