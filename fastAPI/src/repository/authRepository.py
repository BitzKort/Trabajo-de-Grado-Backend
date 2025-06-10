import asyncpg
from fastapi import HTTPException, status
from loguru import logger
from src.schemas.authSchemas import EmailCheckerResponse, Token, Id

async def emailCheckerRepository(email, dbConect: asyncpg.Pool) -> str:

    """
        Método para verificar el usuario por medio del correo electrónico.

        Retorna
        -------
        Un objeto EmailCheckerResponse con el id y la contraseña.

        Excepciones
        -------
        - 404 not found: Si el usuario o contraseña son incorrectos.
        - Excepciones de conexión a la bd.


    """


    query = "SELECT id, password FROM users WHERE email = $1;"

    try:
        async with dbConect.acquire() as conn:

            result = await conn.fetchrow(query,email)

            if result:


                userData = EmailCheckerResponse(**dict(result))

                return userData
            
            else:

                logger.error("Usuario {} no encontrado".format(email))

                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario o contraseña incorrectos")

    except Exception as e:

        raise e


async def get_userid_by_email(email, dbConect: asyncpg.Pool) -> Id:

    """
        Método para verificar el usuario por correo electronico.

        Retorna
        -------
        Un objeto Id con el id del usuario.

        Excepciones
        -------
        - 404 not found: Si No hay una cuenta con ese correo electrónico.

    """

    query ="SELECT id FROM users WHERE email = $1;"

    try:

        async with dbConect.acquire() as conn:

            response = await conn.fetchrow(query, email)

            response = Id(**dict(response))

            return response
            
    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay una cuenta con este correo electrónico.")
    

async def set_password_recovery(email, token, dbConect: asyncpg.Pool) -> Token:

    """
        Método para ingresar el token de recuperación de contraseña del usuario.

        Retorna
        -------
        Un objeto Token con el token de recuperación de contraseña (el token es un uuid de TSID).

        Excepciones
        -------
        - Excepciones de conexión a la bd.

    """

    query ="UPDATE users SET password_recovery = $2 WHERE id = $1 RETURNING password_recovery AS token;"

    try:

        async with dbConect.acquire() as conn:

            response = await conn.fetchrow(query, email, token)

            response = Token(**dict(response))

            return response
            
    except Exception as e:
        
        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)


async def verify_token_recovery(token_recovery, dbConect: asyncpg.Pool) -> Id:

    """
        Método para verificar que el token de recuperación de contraseña del usuario esté en la base de datos.

        Retorna
        -------
        Un objeto Token con el token de recuperación de contraseña (el token es un uuid de TSID).

        Excepciones
        -------
        - 401 UNAUTHORIZED si no es el mismo token que se envió en el correo.
        - Excepciones de conexión a la bd.

    """

    query ="SELECT id FROM users WHERE password_recovery = $1;"

    try:

        async with dbConect.acquire() as conn:

            response = await conn.fetchrow(query, token_recovery)


            if not response:

                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="URL no valida.")

            response = Id(**dict(response))

            return response
            
    except Exception as e:
        logger.error(e)
        raise e
    

async def delete_token_recovery(email, dbConect: asyncpg.Pool):

    """
        Método para borrar el token de recuperación de contraseña del usuario.

        Retorna
        -------
        None

        Excepciones
        -------
        - Excepciones de conexión a la bd.

    """

    query ="UPDATE users SET password_recovery = NULL WHERE id = $1;"

    try:

        async with dbConect.acquire() as conn:

            await conn.fetchrow(query, email)

    except Exception as e:

        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

