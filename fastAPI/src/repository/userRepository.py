

from loguru import logger

from src.schemas.userSchema import userNameResponse



async def getUserName(id, db):

    query ="SELECT name, username FROM users WHERE id = $1;"


    try:

        async with db.acquire() as conn:

            response = await conn.fetchrow(query, id)

            response = userNameResponse(**dict(response))

            return response
            
    except Exception as e:

        logger.error(e)

