from celery import Celery
import os
import dotenv

dotenv.load_dotenv(".env")


celery = Celery(
    "task",
    broker= os.getenv("REDIS_BROKER_URL"),
    include=["src.task.celery_task"],
    backend=os.getenv("REDIS_BACKEND_URL")
)

celery.conf.beat_schedule = {
    "generate-lessons-10-min": {
        "task": "src.task.celery_task.generate_lessons",
        "schedule": 180.0
        }
}

celery.conf.update(
    worker_concurrency=3,
    worker_prefetch_multiplier=4,
    broker_pool_limit=10
)