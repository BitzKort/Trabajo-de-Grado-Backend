import asyncpg
from fastapi import HTTPException, status
from loguru import logger
from src.schemas.authSchemas import EmailCheckerResponse, Token, Id

async def emailCheckerRepository(email, dbConect: asyncpg.Pool) -> str:

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

        logger.warning(f"Error buscando usuario {e}")

        raise e


async def get_userid_by_email(email, dbConect: asyncpg.Pool) -> Id:

    query ="SELECT id FROM users WHERE email = $1;"

    try:

        async with dbConect.acquire() as conn:

            response = await conn.fetchrow(query, email)

            response = Id(**dict(response))

            return response
            
    except Exception as e:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay una cuenta con este correo electrónico.")
    

async def set_password_recovery(email, token, dbConect: asyncpg.Pool) -> Token:

    query ="UPDATE users SET password_recovery = $2 WHERE id = $1 RETURNING password_recovery AS token;"

    try:

        async with dbConect.acquire() as conn:

            response = await conn.fetchrow(query, email, token)

            response = Token(**dict(response))

            return response
            
    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)


async def verify_token_recovery(token_recovery, dbConect: asyncpg.Pool) -> Id:

    query ="SELECT id FROM users WHERE password_recovery = $1;"

    try:

        async with dbConect.acquire() as conn:

            response = await conn.fetchrow(query, token_recovery)


            if not response:

                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="URL no valida.")

            response = Id(**dict(response))

            return response
            
    except Exception as e:

        raise e
    

async def delete_token_recovery(email, dbConect: asyncpg.Pool) -> Token:

    query ="UPDATE users SET password_recovery = NULL WHERE id = $1;"

    try:

        async with dbConect.acquire() as conn:

            await conn.fetchrow(query, email)

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

