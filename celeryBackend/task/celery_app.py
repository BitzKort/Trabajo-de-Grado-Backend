import os
import dotenv
import random
import time
from celery import Celery
from celery.signals import worker_process_init, worker_ready
from celery.schedules import crontab

dotenv.load_dotenv(dotenv_path="../.env.dev")


celery = Celery(
    "task",
    broker= os.getenv("REDIS_BROKER_URL"),
    include=["task.celery_task"],
    backend=os.getenv("REDIS_BACKEND_URL")
)


celery.conf.beat_schedule = {
    "generate-lessons-10-min": {
        "task": "task.celery_task.generate_lessons",
        "schedule": 200
        }
}

celery.conf.update(
    worker_concurrency=3,
    worker_prefetch_multiplier=4,
    broker_pool_limit=12,
)

@worker_process_init.connect
def init_pools(**kwargs):
    random.seed(os.getpid() + int(time.time()))


