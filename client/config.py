import os
from dotenv import load_dotenv

# Load the single client env
load_dotenv(override=True)

CLIENT_ROLE = os.environ.get("CLIENT_ROLE", "user").lower()  # default to 'user'

def get_env_var(name: str, cast=str):
    value = os.environ.get(name)
    if value is None:
        raise RuntimeError(f"Environment variable '{name}' is required but not set.")
    if cast == bool:
        val = value.lower()
        if val in ("true", "1"):
            return True
        elif val in ("false", "0"):
            return False
        else:
            raise ValueError()
    return cast(value)

class Config:
    SERVER_URL = get_env_var("SERVER_URL")
    API_PREFIX = get_env_var("API_PREFIX")
    APP_VERSION = get_env_var("APP_VERSION")

    if CLIENT_ROLE == "admin":
        CLIENT_CONT = get_env_var("ADMIN_CLIENT_CONT")
        CLIENT_PORT = get_env_var("ADMIN_CLIENT_PORT", int)
        TRUSTED_MODE = get_env_var("ADMIN_TRUSTED_MODE", bool)
    else:
        CLIENT_CONT = get_env_var("USER_CLIENT_CONT")
        CLIENT_PORT = get_env_var("USER_CLIENT_PORT", int)
        TRUSTED_MODE = get_env_var("USER_TRUSTED_MODE", bool)
