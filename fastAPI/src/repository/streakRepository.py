import asyncpg
from fastapi import HTTPException, status
from loguru import logger
from src.schemas.userSchema import UserInfoResponse


async def update_strike(userInfo, dbConect: asyncpg.pool):

    query =" UPDATE streaks SET days = $2, exp = $3, last_activity_date = $4 WHERE id = $1 RETURNING * ;"

    try:

        async with dbConect.acquire() as conn:

            DBResponse = await conn.fetchrow(query, userInfo.id, userInfo.dias, userInfo.exp, userInfo.last_activity_date)

            UserResponse = UserInfoResponse(**dict(DBResponse))

            return UserResponse
        
    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)



async def get_last_activity_day(userId: str, dbConnect):
    query = """
        SELECT last_activity_day FROM users WHERE id = $1;
    """

    try:
        async with dbConnect.acquire() as conn:
            row = await conn.fetchrow(query, userId)
            if row:
                return row["last_activity_day"]
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado."
                )

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo la última actividad del usuario."
        )


async def update_days(user_id: str, dbConnect):
   
    query = """
        UPDATE streaks SET days = days + 1 WHERE id = $1;
    """

    try:
        async with dbConnect.acquire() as conn:
            await conn.execute(query, user_id)

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error actualizando los dias del usuario."
        )


async def update_exp(userId, newExp, newLastTime, dbConect: asyncpg.pool):


    query =" UPDATE streaks SET exp = exp + $2, last_activity_date = $3 WHERE id = $1;"

    try:

        async with dbConect.acquire() as conn:

            await conn.fetchrow(query, userId, newExp, newLastTime)
        
    except Exception as e:
                
        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

