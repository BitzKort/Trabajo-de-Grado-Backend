from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown
from celery.schedules import crontab
from src.repository.dbConection import init_postgres, get_postgres, close_postgres
import os
import dotenv

dotenv.load_dotenv(dotenv_path="../.env.prod")


celery = Celery(
    "task",
    broker= os.getenv("REDIS_BROKER_URL"),
    include=["task.celery_task"],
    backend=os.getenv("REDIS_BACKEND_URL")
)


celery.conf.beat_schedule = {
    "generate-lessons-10-min": {
        "task": "task.celery_task.generate_lessons",
        "schedule": 180.0
        },
    "backend-cleanup-every-10-min": {
        "task": "celery.backend_cleanup",
        "schedule": crontab(minute="*/10")  # Cada 10 minutos
    }
}

celery.conf.update(
    worker_concurrency=3,
    worker_prefetch_multiplier=4,
    broker_pool_limit=10,
    result_expires=600
)

@worker_process_init.connect
def init_pools(**kwargs):
    init_postgres()

@worker_process_shutdown.connect
def shutdown_pools(**kwargs):
    close_postgres()