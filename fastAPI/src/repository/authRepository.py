from fastapi import Depends, HTTPException, status
from loguru import logger
import asyncpg
from src.schemas.authSchemas import EmailCheckerResponse, ForgotPasswordRequest, Token, Id

async def emailCheckerRepository(email, dbConect: asyncpg.Pool) -> str:

    query = "SELECT id, password FROM users WHERE email = $1;"

    try:
        async with dbConect.acquire() as conn:

            result = await conn.fetchrow(query,email)

            if result:

                userData = EmailCheckerResponse(**dict(result))

                return userData
            
            else:

                logger.warning("user {} not found".format(email))

    except Exception as e:

        logger.warning(f"Error fetching user {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during the user auth"
        )


async def get_userid_by_email(email, dbConect: asyncpg.Pool) -> Id:

    query ="SELECT id FROM users WHERE email = $1;"

    try:

        async with dbConect.acquire() as conn:

            response = await conn.fetchrow(query, email)

            response = Id(**dict(response))

            return response
            
    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    

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

            response = Id(**dict(response))

            return response
            
    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    

async def delete_token_recovery(email, dbConect: asyncpg.Pool) -> Token:

    query ="UPDATE users SET password_recovery = NULL WHERE id = $1;"

    try:

        async with dbConect.acquire() as conn:

            await conn.fetchrow(query, email)

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

