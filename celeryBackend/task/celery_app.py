import os
import dotenv
import random
import time
from celery import Celery
from celery.signals import worker_process_init, worker_ready
from celery.schedules import crontab



dotenv.load_dotenv(dotenv_path="../.env.dev")



"""
    Objeto principal del programa 
"""
celery = Celery(
    "task",
    broker= os.getenv("REDIS_BROKER_URL"),
    include=["task.celery_task"],
    backend=os.getenv("REDIS_BACKEND_URL")
)





"""
    Uso de celery beat para generar lecciones cada 15 minutos

    NOTA
    -----
    Al ser un prototipo se realizan las lecciones cada 15 minutos para probar su funcionalidad.

"""
celery.conf.beat_schedule = {
    "generate-lessons-15-min": {
        "task": "task.celery_task.generate_lessons",
        "schedule": 900
        }
}




"""
    Configuracion del worker
"""
celery.conf.update(
    worker_concurrency=3,
    worker_prefetch_multiplier=4,
    broker_pool_limit=12,
)


@worker_process_init.connect
def init_pools(**kwargs):

    """
    Al inicio de cada worker se le da una semilla de generacion diferente con el fin de no tener problemas con los generadores
    de numeros pseudoaleatorios dentro de las tareas.

    """

    random.seed(os.getpid() + int(time.time()))


