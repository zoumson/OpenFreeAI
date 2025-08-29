import os

class Config:
    # Flask & SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///models.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # LLM API key (keep secret)
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

    # Base URL for LLM API
    LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")

    # Redis config for queue
    REDIS_HOST = os.environ.get("REDIS_HOST", "redis")  # service name in docker-compose
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

    # App version
    APP_VERSION = "1.0.0"

    # Optional: queue name
    QUEUE_NAME = os.environ.get("QUEUE_NAME", "prompts")
