from src.schemas.userSchema import UserInfoResponse
from fastapi import HTTPException, status
import asyncpg
from loguru import logger
from tsidpy import TSID


async def update_strike(userInfo, dbConect: asyncpg.pool):

    query =" UPDATE racha SET dias = $2, exp = $3, last_activity_date = $4 WHERE id = $1 RETURNING * ;"

    try:

        async with dbConect.acquire() as conn:

            DBResponse = await conn.fetchrow(query, userInfo.id, userInfo.dias, userInfo.exp, userInfo.last_activity_date)

            UserResponse = UserInfoResponse(**dict(DBResponse))

            return UserResponse
        
    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    

async def update_exp(userId, newExp, newLastTime, dbConect: asyncpg.pool):

    query =" UPDATE racha SET exp = exp + $2, last_activity_date = $3 WHERE id = $1;"

    try:

        async with dbConect.acquire() as conn:

            await conn.fetchrow(query, userId, newExp, newLastTime)
        
    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

