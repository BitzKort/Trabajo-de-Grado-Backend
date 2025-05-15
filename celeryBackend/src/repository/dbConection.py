import os
import psycopg2
from psycopg2 import pool
from loguru import logger
import dotenv

# Pool síncrono de psycopg2
conn_pool: pool.SimpleConnectionPool | None = None

dotenv.load_dotenv(dotenv_path="../.env.prod")


def init_postgres() -> None:
    """
    Inicializa el pool síncrono de PostgreSQL.
    """
    global conn_pool
    if conn_pool is not None:
        return

    try:
        logger.info("Inicializando pool de PostgreSQL…")
        conn_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=os.getenv("DATABASE_URL")
        )
        logger.info("Pool de PostgreSQL creado con éxito.")
    except Exception as e:
        logger.error(f"Error inicializando pool de PostgreSQL: {e}")
        raise

def get_postgres_conn() -> psycopg2.extensions.connection:
    """
    Obtiene y devuelve una conexión del pool de PostgreSQL.
    El llamador es responsable de liberar la conexión con `release_postgres_conn()`.
    """
    if conn_pool is None:
        logger.error("Pool de PostgreSQL no inicializado.")
        raise ConnectionError("Pool de PostgreSQL no inicializado.")
    try:
        return conn_pool.getconn()
    except Exception as e:
        logger.error(f"No se pudo obtener conexión: {e}")
        raise


def release_postgres_conn(conn: psycopg2.extensions.connection) -> None:
    """
    Devuelve una conexión al pool de psycopg2.
    """
    global conn_pool
    if conn_pool is None:
        raise ConnectionError("Pool de PostgreSQL no inicializado.")
    try:
        conn_pool.putconn(conn)
    except Exception as e:
        logger.error(f"Error al liberar conexión al pool: {e}")
        raise


def close_postgres() -> None:
    """
    Cierra todas las conexiones del pool de PostgreSQL.
    """
    global conn_pool
    if conn_pool:
        try:
            logger.info("Cerrando pool de PostgreSQL…")
            conn_pool.closeall()
            conn_pool = None
            logger.info("Pool de PostgreSQL cerrado con éxito.")
        except Exception as e:
            logger.error(f"Error cerrando pool de PostgreSQL: {e}")
            raise
    else:
        logger.warning("Pool de PostgreSQL ya estaba cerrado.")