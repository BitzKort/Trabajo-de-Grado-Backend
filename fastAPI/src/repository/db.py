import os
import asyncpg
import redis.asyncio as asyncredis
from loguru import logger
from typing import Optional


conn_pool: Optional[asyncpg.Pool] = None
redis_client_pool: asyncredis.Redis


async def init_postgres() -> None:
    """
        Inicia la conexión a la base de datos.

        Esta función se debe de llamar al iniciar el servidor para inicializar la conexión.

        Retorna
        -------
        None

    """
    global conn_pool
    try:
        logger.info("Iniciando la conexión a la base de datos...")

        conn_pool = await asyncpg.create_pool(
            dsn=os.getenv("DATABASE_URL"), min_size=1, max_size=10
        )
        logger.info("Conexión a la base de datos creada con éxito.")

    except Exception as e:
        logger.error(f"Error Iniciando la conexión a la base de datos: {e}")
        raise


async def get_postgres() -> asyncpg.Pool:
    """
        Retorna el pool de conexiones PostgreSQL.

        Esta función devuelve el objeto pool de conexiones, desde el cual se pueden adquirir
        Conexiones individuales se pueden adquirir según sea necesario para las operaciones de base de datos.

        Retorna
        -------
        asyncpg.Pool
            El objeto pool de conexiones a la base de datos PostgreSQL.

    """
    global conn_pool
    if conn_pool is None:
        logger.error("Conexión no iniciada")
        raise ConnectionError("Conexión a la base de datos no iniciada.")
    try:
        return conn_pool
    except Exception as e:
        logger.error(f"Error retornando la conexión a la base de datos: {e}")
        raise



async def close_postgres() -> None:
    """
        Cierra las conexiones de la base de datos.

        Esta función debe ser llamada durante el cierre de la aplicación FastAPI
        para cerrar correctamente todas las conexiones del pool y liberar recursos.
    """
    global conn_pool
    if conn_pool is not None:
        try:
            logger.info("Cerrando Conexión a la base de datos...")
            await conn_pool.close()
            logger.info("Conexión a la base de datos cerrada con éxito.")
        except Exception as e:
            logger.error(f"Error cerrando la conexión a la base de datos: {e}")
            raise
    else:
        logger.warning("Conexión a la base de datos no iniciada.")



async def init_redis():

    """
        Inicia la conexión a redis.

        Esta función se debe de llamar al iniciar el servidor para inicializar la conexión.

        Retorna
        -------
        None

    """
    

    global redis_client_pool 

    try:

        redis_client_pool= asyncredis.from_url(
            os.getenv("REDIS_BACKEND_URL"),
            encoding="utf-8", decode_responses=True
        )

        await redis_client_pool.ping()

        logger.success("Conexión a redis creada con éxito.")

    except Exception as e:
        logger.error(f"Error creando la conexión a redis: {e}")


async def get_redis():

    """
        Retorna la conexión a la base de datos.

        Retorna
        -------
            asyncredis.Redis
            El objeto pool de conexiones a la base de datos PostgreSQL.

    """


    global redis_client_pool
    if redis_client_pool is None:
        logger.error("Conexión a redis no iniciada.")
        raise ConnectionError("Conexión a redis no iniciada.")
    try:
        return redis_client_pool
    except Exception as e:
        logger.error(f"Error retornando la conexión a redis: {e}")
        raise


async def close_redis():

    """
        Cierra las conexiones de redis.

        Esta función debe ser llamada durante el cierre de la aplicación FastAPI
        para cerrar correctamente todas las conexiones y liberar recursos.
    """

    global redis_client_pool
    if redis_client_pool is None:
        logger.warning("Conexión a redis no iniciada.")
        return

    try:
        await redis_client_pool.aclose()
        logger.info("Conexión a redis creada con éxito.")
    except Exception as e:
        logger.error(f"Error cerrando la conexión a redis: {e}")
        raise