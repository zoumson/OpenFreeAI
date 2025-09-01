# server/infrastructure/celery_app.py
from celery import Celery
from server.config import Config

# Create a single Celery instance
celery_app = Celery(
    "server",
    broker=f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/0",
    backend=f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/1"
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
