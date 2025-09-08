from celery import Celery
from server.config import Config

celery_app = Celery(
    "server",
    broker=f"redis://:{Config.REDIS_PASSWORD}@{Config.REDIS_HOST}:{Config.REDIS_PORT}/0",
    backend=f"redis://:{Config.REDIS_PASSWORD}@{Config.REDIS_HOST}:{Config.REDIS_PORT}/1"
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Auto-discover tasks in the jobs package
celery_app.autodiscover_tasks(["server.jobs"])
