from redis import Redis
from rq import Worker, Queue, Connection
from server.config import Config
import os

# Queue name
listen = [Config.QUEUE_NAME]

# Redis connection
redis_url = f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}"
conn = Redis.from_url(redis_url)

if __name__ == "__main__":
    print(f"Starting worker listening on queue: {listen[0]} with Redis {redis_url}")
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
