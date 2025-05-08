from fastapi import Depends, HTTPException
from loguru import logger
from src.repository.db import get_postgres
import asyncpg
from tsidpy import TSID

from src.schemas.userSchema import EmailCheckerResponse, userNameResponse

async def emailCheckerRepository(email, dbconect) -> str:

    query = "SELECT id, password FROM users WHERE email = $1;"

    try:
        async with dbconect.acquire() as conn:

            result = await conn.fetchrow(query,email)

            if result:

                response = EmailCheckerResponse(**dict(result))

                

                return response
            
            else:

                logger.warning("user {} not found".format(email))

                raise HTTPException(
                    status_code=500, detail="user not found"
                )
    except Exception as e:

        logger.warning(f"Error fetching user {e}")

        raise HTTPException(
            status_code=500, detail="Internal server error during the user auth"
        )

async def createUserRepository(userData, dbconect):

    id = str(TSID.create())

    query ="INSERT INTO users (id, name, username, email, password) VALUES (($1)::text, $2, $3, $4, $5);"


    try: 
        async with dbconect.acquire() as conn:

            await conn.fetchrow(
                query,
                id,
                userData.name,
                userData.username,
                userData.email,
                userData.password
            )

            logger.success("usuario creado exitosamente")

            return {"msg": "usuario creado exitosamente"}

            

            
            
    except Exception as e:
        logger.error(f"Error on insert user: {e}")


