import logging

logger = logging.getLogger(__name__)

_broker_checked = False
_broker_available = False


def safe_celery_delay(task_path: str, *args, **kwargs):
    """Attempt to dispatch a Celery task. If broker is unavailable, skip silently."""
    global _broker_checked, _broker_available

    if _broker_checked and not _broker_available:
        return False

    try:
        import importlib
        module_path, task_name = task_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        task = getattr(module, task_name)
        task.apply_async(args=args, kwargs=kwargs, timeout=3)
        _broker_checked = True
        _broker_available = True
        return True
    except Exception as e:
        _broker_checked = True
        _broker_available = False
        logger.debug("Celery broker unavailable, skipping task %s: %s", task_path, e)
        return False
