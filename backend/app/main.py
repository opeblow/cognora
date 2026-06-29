from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import settings
from app.middleware.cors import setup_cors
from app.middleware.rate_limit import RateLimitMiddleware
from app.routes.api import auth, subjects, ai, quizzes, exams, dashboard, credits, lessons
from app.database.base import engine, Base


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    setup_cors(app)
    app.add_middleware(RateLimitMiddleware)

    app.include_router(auth.router, prefix="/api")
    app.include_router(subjects.router, prefix="/api")
    app.include_router(ai.router, prefix="/api")
    app.include_router(quizzes.router, prefix="/api")
    app.include_router(exams.router, prefix="/api")
    app.include_router(dashboard.router, prefix="/api")
    app.include_router(credits.router, prefix="/api")
    app.include_router(lessons.router, prefix="/api")

    @app.get("/api/health")
    def health_check():
        return {"status": "healthy", "version": settings.APP_VERSION}

    return app


app = create_app()
