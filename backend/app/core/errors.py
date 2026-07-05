import uuid
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.config import settings


class AppError(Exception):
    def __init__(self, code: str, message: str, status: int = 400, detail: dict | None = None):
        self.code = code
        self.message = message
        self.status = status
        self.detail = detail or {}


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
                "request_id": getattr(request.state, "request_id", None),
            }
        },
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    import logging
    logger = logging.getLogger(__name__)
    logger.exception("Unhandled error")
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            sentry_sdk.capture_exception(exc)
        except ImportError:
            logger.warning("SENTRY_DSN is set but sentry_sdk is not installed. Install with: pip install sentry-sdk")
        except Exception as e:
            logger.error(f"Failed to send error to Sentry: {e}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "request_id": getattr(request.state, "request_id", None),
            }
        },
    )
