from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "newsletter",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.timezone = "UTC"
