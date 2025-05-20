
import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.repository.db import get_postgres
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


