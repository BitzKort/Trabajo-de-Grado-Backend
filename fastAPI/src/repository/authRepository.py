from fastapi import Depends, HTTPException, status
from loguru import logger
import asyncpg
from tsidpy import TSID

from src.schemas.authSchemas import EmailCheckerResponse, RegisterValidation

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

async def createUserRepository(userData, dbConect: asyncpg.Pool) -> RegisterValidation:

    id = str(TSID.create())

    query ="INSERT INTO users (id, name, username, email, password) VALUES (($1)::text, $2, $3, $4, $5) RETURNING id AS userid;"


    try: 
        async with dbConect.acquire() as conn:

           new_user = await conn.fetchrow(
                query,
                id,
                userData.name,
                userData.username,
                userData.email,
                userData.password
            )
                      
           user = RegisterValidation(**dict(new_user))
           
           logger.success("user created")

           return user 

    except Exception as e:
        logger.error(f"Error on insert user: {e}")


