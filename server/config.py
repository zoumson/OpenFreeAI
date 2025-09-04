import os

# Ensure data directory exists for SQLite
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

class Config:
    # -----------------------------
    # Flask & SQLAlchemy
    # -----------------------------
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        f"sqlite:///{os.path.join(DATA_DIR, 'llm.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -----------------------------
    # LLM API key & Base URL
    # -----------------------------
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")

    # -----------------------------
    # Redis configuration
    # -----------------------------
    REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

    # -----------------------------
    # Flask server host & port
    # -----------------------------
    FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))

    # -----------------------------
    # Celery / Queue
    # -----------------------------
    QUEUE_NAME = os.environ.get("QUEUE_NAME", "prompts")

    # -----------------------------
    # API prefix and version
    # -----------------------------
    API_PREFIX = "/api/v1"
    APP_VERSION = "1.0.0"

    # -----------------------------
    # Shared folder path (optional)
    # -----------------------------
    SHARED_DIR = os.environ.get("SHARED_DIR", "/app/server/shared")
