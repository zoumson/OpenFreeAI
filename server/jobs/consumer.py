# consumer.py
from redis import Redis
from rq import Worker, Queue
from server.config import Config
from server.app import create_app

# Queue name(s)
listen = [Config.QUEUE_NAME]

# Redis connection
redis_url = f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}"
conn = Redis.from_url(redis_url)

if __name__ == "__main__":
    # Create Flask app and push context so current_app works in tasks
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    print(f"Starting worker listening on queue: {listen[0]} with Redis {redis_url}")

    # Create queues with the Redis connection
    queues = [Queue(name, connection=conn) for name in listen]

    # Start the worker
    worker = Worker(queues)
    worker.work()
