# server/infrastructure/redis.py
from redis import Redis
from server.config import Config

# Single Redis connection for the whole app
redis_conn = Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    decode_responses=True  # Optional: return strings instead of bytes
)
