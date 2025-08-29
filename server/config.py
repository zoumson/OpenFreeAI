import os

class Config:
    # Flask & SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///models.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # LLM API key (keep secret)
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    # Base URL for OpenAI or compatible LLM API
    LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")
