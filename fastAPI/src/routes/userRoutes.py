
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from src.repository.db import get_postgres
from src.schemas.userSchema import User, UserInfoResponse, UserInfoEntry
from typing import List, Annotated
import asyncpg
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

        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve products")



@userRouter.post("/userInfo", response_model=UserInfoResponse)
async def getUserInfo(id: Annotated[UserInfoEntry, Query(...)], user_data: UserInfoResponse = Depends(userInfo))-> UserInfoResponse:

    user_info, dbConnect = user_data

    streak_data_verified = await verify_streak(user_info, dbConnect)

    return streak_data_verified

@userRouter.put("/updateUser", status_code=status.HTTP_200_OK)

async def update_user(userData = Depends(updateUser)):

    
    return userData


