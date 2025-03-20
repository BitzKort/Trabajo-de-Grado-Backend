
from loguru import logger

logger.info("Descargando todos los modelos")

# Para cada modelo, se crea un logger "vinculado" que añade contexto extra
modelos = ["modelo1", "modelo2", "modelo3"]
with logger.contextualize(proceso="inicializando modelos"):
    logger.info("Descargando todos los modelos")
    for nombre in modelos:
        with logger.contextualize(modelo=nombre):
            logger.info("Iniciando el modelo")



#si ves esto en el futuro, olvidalo da igual xd