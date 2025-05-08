
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from src.repository.db import get_postgres
from src.schemas.userSchema import User, Login, Register, LoginResponse, UserInfoResponse, UserInfoEntry
from typing import List, Annotated
import asyncpg
from loguru import logger

from src.services.authServices import authLogin, createUserService

from src.services.userServices import userInfoService


userRouter = APIRouter()



@userRouter.get("/getUsers", response_model=List[User])
async def test(dbConect: asyncpg.Pool = Depends(get_postgres)) -> List[User]:


    query = "SELECT * from users;"

    try:

        async with dbConect.acquire() as conn:

            results = await conn.fetch(query)
            return [User(**dict(result)) for result in results]
    
    except Exception as e:

        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve products")


@userRouter.post("/loginUser", response_model=LoginResponse)
async def login(user: Login, dbConect: asyncpg.Pool = Depends(get_postgres))->LoginResponse:


    response = await authLogin(user, dbConect)

    if not response:

        raise HTTPException (status_code=404, detail="usuario no encontrado")
    
    return response

@userRouter.post("/register")

async def register(userData:Register, dbConect: asyncpg.Pool = Depends(get_postgres)):

    response = await createUserService(userData, dbConect)

    if not response:

        logger.error("something went wrong at creating user")

        raise HTTPException (status_code=500, detail="error durante el registro")
    
    else:
        return response


@userRouter.post("/userInfo", response_model=UserInfoResponse)

async def userInfo(id: Annotated[str, Query(...)], db: asyncpg = Depends(get_postgres))-> UserInfoResponse:

    logger.warning("entra al router info")

    response = await userInfoService(id, db)


    logger.warning("vuelve exitosamente")

    return response


    

