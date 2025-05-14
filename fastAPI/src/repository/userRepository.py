
from src.schemas.userSchema import userNameResponse, UserInfoResponse
from fastapi import HTTPException, status
import asyncpg


async def getUserName(id, dbConect: asyncpg.Pool) -> userNameResponse:

    query ="SELECT name, username FROM users WHERE id = $1;"

    try:

        async with dbConect.acquire() as conn:

            response = await conn.fetchrow(query, id)

            response = userNameResponse(**dict(response))

            return response
            
    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)


async def getUserInfo(id, dbConect: asyncpg.Pool) -> UserInfoResponse:
    
    query =" SELECT u.name, u.username, r.exp, r.dias,  DENSE_RANK() OVER (ORDER BY r.exp DESC) AS ranking FROM racha r INNER JOIN users u ON r.id = u.id WHERE u.id = $1;"

    try:

        async with dbConect.acquire() as conn:

            DBResponse = await conn.fetchrow(query, id)

            UserResponse = UserInfoResponse(**dict(DBResponse))

            return UserResponse
        
    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)


async def update_strike(userInfo, dbConect: asyncpg.pool):

    pass