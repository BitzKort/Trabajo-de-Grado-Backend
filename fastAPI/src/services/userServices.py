
from loguru import logger
from fastapi import HTTPException
from src.schemas.userSchema import UserInfoResponse
from src.repository.userRepository import getUserName

async def userInfoService(id, db):

    print(id)
    print(type(id))

    logger.warning("entra al router info services")

    
    query =" SELECT u.name, u.username, r.exp, r.dias,  DENSE_RANK() OVER (ORDER BY r.exp DESC) AS ranking FROM racha r INNER JOIN users u ON r.id = u.id WHERE u.id = $1;"

    try:

        async with db.acquire() as conn:

            response = await conn.fetchrow(query, id)

            r1 = UserInfoResponse(**dict(response))

            logger.info("respuesta del ranking: {}".format(r1))

            return r1
        
    except Exception as e:

        response = await getUserName(id, db)

        logger.warning(response)

        return UserInfoResponse(name=response.name, username=response.username, exp=0, dias=0, ranking=0)

    