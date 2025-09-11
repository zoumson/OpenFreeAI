
# SERVER_URL = "http://127.0.0.1:5000"  # Server root
# API_PREFIX = "/api/v1"                # API version prefix

# client/config.py
import os
from dotenv import load_dotenv

# Load .env file in the client folder
load_dotenv(override=True)

def get_env_var(name: str, cast=str) -> any:
    """Get an environment variable, enforce existence, and cast type."""
    value = os.environ.get(name)
    if value is None:
        raise RuntimeError(f"Environment variable '{name}' is required but not set.")
    
    try:
        if cast == bool:
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
    # Server URL
    SERVER_URL = get_env_var("SERVER_URL")
    API_PREFIX = get_env_var("API_PREFIX")

    # Optional client-side settings
    TRUSTED_MODE = get_env_var("TRUSTED_MODE", bool)

    # UI port for running client container
    UI_PORT = get_env_var("UI_PORT", int)

    # App version
    APP_VERSION = get_env_var("APP_VERSION", str)
