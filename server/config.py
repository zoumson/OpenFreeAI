import os

class Config:
    # Flask & SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///models.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # LLM API key
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

    # Base URL for LLM API
    LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")

    # Redis config
    REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

    # Flask server host & port (server-side only)
    FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")  # bind to all interfaces inside container
    FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))

    # Optional: queue name
    QUEUE_NAME = os.environ.get("QUEUE_NAME", "prompts")

    # Optional API prefix
    API_PREFIX = "/api/v1"

    # App version
    APP_VERSION = "1.0.0"
