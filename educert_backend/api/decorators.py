import logging
from functools import wraps

logger = logging.getLogger(__name__)

def log_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            logger.exception(f"Exception in {func.__name__}")
            raise
    return wrapper