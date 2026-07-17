from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "cognora",
    broker=settings.CELERY_BROKER_URL or settings.broker_redis_url,
    backend=settings.CELERY_RESULT_BACKEND_URL or settings.broker_redis_url,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    broker_connection_timeout=5,
    broker_connection_retry_on_startup=True,
    broker_transport_options={"connect_timeout": 5},
    task_routes={
        "app.workers.tasks.reset_weekly_credits": {"queue": "cpu"},
        "app.workers.tasks.cleanup_expired_tokens": {"queue": "cpu"},
        "app.workers.tasks.send_email": {"queue": "io"},
        "app.workers.tasks.process_ocr": {"queue": "io"},
        "app.workers.tasks.transcribe_audio": {"queue": "io"},
        "app.workers.tasks.pre_generate_textbook_sections": {"queue": "io"},
        "app.workers.tasks.review_content_issue": {"queue": "io"},
        "app.workers.tasks.pre_generate_question_pool": {"queue": "io"},
    },
    beat_schedule={
        "reset-weekly-credits": {
            "task": "app.workers.tasks.reset_weekly_credits",
            "schedule": 604800,  # 7 days
            "args": (),
        },
        "cleanup-expired-tokens": {
            "task": "app.workers.tasks.cleanup_expired_tokens",
            "schedule": 86400,  # 24 hours
            "args": (),
        },
        "pre-generate-textbook-sections": {
            "task": "app.workers.tasks.pre_generate_textbook_sections",
            "schedule": 43200,  # 12 hours
            "args": (),
        },
        "pre-generate-question-pool": {
            "task": "app.workers.tasks.pre_generate_question_pool",
            "schedule": 3600,  # 1 hour
            "args": (),
        },
    },
)
