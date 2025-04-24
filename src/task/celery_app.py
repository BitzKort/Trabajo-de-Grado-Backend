from celery import Celery
import os
import dotenv

dotenv.load_dotenv(".env")


celery = Celery(
    "task",
    broker= os.getenv("REDIS_URL"),
    include=["src.task.celery_task"]
)

celery.conf.beat_schedule = {
    "generate-lessons-10-min": {
        "task": "src.task.celery_task.generate_lessons",
        "schedule": 600.0
        }
}