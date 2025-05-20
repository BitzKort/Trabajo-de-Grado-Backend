
import asyncpg
import redis.asyncio as asyncredis
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.repository.db import get_postgres, get_redis
from src.schemas.userSchema import User, UserInfoResponse, UserInfoEntry
from typing import List, Annotated
from loguru import logger
from src.services.authServices import get_current_user
from src.services.userServices import userInfo, verify_streak, updateUser


userRouter = APIRouter()



@userRouter.get("/getUsers", response_model=List[User])
async def test(dbConect: asyncpg.Pool = Depends(get_postgres), token:str = Depends(get_current_user)) -> List[User]:


    query = "SELECT * from users;"

    try:

        async with dbConect.acquire() as conn:

            results = await conn.fetch(query)
            return [User(**dict(result)) for result in results]
    
    except Exception as e:

        logger.error(f"Error encontrando el usuario: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)



@userRouter.post("/userInfo", response_model=UserInfoResponse)
async def getUserInfo(id: Annotated[UserInfoEntry, Query(...)], user_data: UserInfoResponse = Depends(userInfo))-> UserInfoResponse:


    try:

        user_info, dbConnect = user_data

        streak_data_verified = await verify_streak(user_info, dbConnect)

        return streak_data_verified

    except Exception as e:
        
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)


@userRouter.put("/updateUser", status_code=status.HTTP_200_OK)

async def update_user(userData = Depends(updateUser)):

    try:
        return userData
    
    except Exception as e:

        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    


@userRouter.delete("/deleteLogicUser")
async def test(userId:str,dbConect: asyncpg.Pool = Depends(get_postgres), redisConnect: asyncredis.Redis = Depends(get_redis),token:str = Depends(get_current_user)):


    query ="UPDATE users SET deleted = $2 WHERE id = $1;"

    try:

        async with dbConect.acquire() as conn:

            await conn.fetchrow(query, userId, True)        
        
        #guardado en redis para verificacion del token        
        key = "deleted:users"

        exists = await redisConnect.exists(key)
        if not exists:
            # crea el SET con el primer miembroe
            await redisConnect.sadd(key, userId)

        else:

            await redisConnect.sadd(key, userId)


        return {"msg": "Usuario eliminado logicamente"}



    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
