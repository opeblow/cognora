import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from app.core.config import settings


def init_sentry():
    if not settings.SENTRY_DSN:
        return

    logging_integration = LoggingIntegration(
        level="warning",
        event_level="error",
    )

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment="production" if not settings.DEBUG else "development",
        release=f"{settings.APP_NAME}@{settings.APP_VERSION}",
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
        integrations=[
            FastApiIntegration(
                failed_request_status_codes=[500, 502, 503, 504],
            ),
            SqlalchemyIntegration(),
            RedisIntegration(),
            logging_integration,
        ],
        before_send=_filter_sensitive_data,
        max_breadcrumbs=50,
        attach_stacktrace=True,
    )


def _filter_sensitive_data(event, hint):
    sensitive_keys = {
        "password", "secret", "token", "api_key", "authorization",
        "credit_card", "ssn", "openai_api_key", "brave_api_key",
        "paystack_secret_key", "google_client_secret",
    }

    if "request" in event:
        headers = event["request"].get("headers", {})
        for key in headers:
            if any(s in key.lower() for s in sensitive_keys):
                headers[key] = "[FILTERED]"

    if "extra" in event:
        for key in list(event["extra"].keys()):
            if any(s in key.lower() for s in sensitive_keys):
                event["extra"][key] = "[FILTERED]"

    return event
