import os
from dotenv import load_dotenv

# Load .env (override ensures any existing env vars are replaced)
load_dotenv(override=True)

def get_env_var(name: str, cast=str) -> any:
    """Get an environment variable, enforce existence, and cast type."""
    value = os.environ.get(name)
    if value is None:
        raise RuntimeError(f"Environment variable '{name}' is required but not set.")
    
    try:
        if cast == bool:
            # Accept 'True', 'true', '1' as True; 'False', 'false', '0' as False
            value_lower = value.lower()
            if value_lower in ("true", "1"):
                return True
            elif value_lower in ("false", "0"):
                return False
            else:
                raise ValueError()
        return cast(value)
    except ValueError:
        raise RuntimeError(f"Environment variable '{name}' must be of type {cast.__name__}, got '{value}'")

class Config:
    # Flask & SQLAlchemy
    SQLALCHEMY_DATABASE_URI = get_env_var("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = get_env_var("SQLALCHEMY_TRACK_MODIFICATIONS", bool)

    # LLM API
    OPENAI_API_KEY = get_env_var("OPENAI_API_KEY")
    LLM_BASE_URL = get_env_var("LLM_BASE_URL")

    # Redis
    REDIS_CONT = get_env_var("REDIS_CONT")
    REDIS_HOST = get_env_var("REDIS_HOST")
    REDIS_PORT = get_env_var("REDIS_PORT", int)
    QUEUE_NAME = get_env_var("QUEUE_NAME")

    # Flask server
    FLASK_CONT = get_env_var("FLASK_CONT")
    FLASK_APP = get_env_var("FLASK_APP")
    FLASK_ENV = get_env_var("FLASK_ENV")
    FLASK_HOST = get_env_var("FLASK_HOST")
    FLASK_PORT = get_env_var("FLASK_PORT", int)

    # Celery
    CELERY_CONT = get_env_var("CELERY_CONT")
    CELERY_AUTOSCALE = get_env_var("CELERY_AUTOSCALE")  # format: "max,min"
    CELERY_APP = get_env_var("CELERY_APP")

    # API
    API_PREFIX = get_env_var("API_PREFIX")

    # App version
    APP_VERSION = get_env_var("APP_VERSION")
