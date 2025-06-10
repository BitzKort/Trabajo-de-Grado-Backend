
import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status
from src.repository.db import get_postgres
from src.schemas.userSchema import UserInfoResponse, UserUpdateModel
from loguru import logger
from src.services.authServices import get_current_user
from src.services.userServices import userInfo, verify_streak, updateUser


userRouter = APIRouter()



@userRouter.get("/userInfo", response_model=UserInfoResponse)
async def getUserInfo(user_data: UserInfoResponse = Depends(userInfo))-> UserInfoResponse:

    """
        Ruta para obtener la información general del usuario.

        Retorna
        -------
        Objeto UserInfoResponse con la información general del usuario.

        Excepciones
        -------
        - Excepciones dentro de los metodos de servicio.
    """

    try:

        user_info, dbConnect = user_data

        streak_data_verified = await verify_streak(user_info, dbConnect)


        return streak_data_verified

    except Exception as e:
        
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)


@userRouter.put("/updateUser", status_code=status.HTTP_200_OK)
async def update_user(userData: UserUpdateModel, userId = Depends(get_current_user), dbConnect:asyncpg.pool = Depends(get_postgres)):
    
    """
        Ruta para actualizar el nombre o el username del usuario.

        Retorna
        -------
        200 ok: mensaje si fue exitoso o no la actualizacion

        Excepciones
        -------
        - Excepciones dentro de los metodos de servicio.
    """


    try:
        userData = await updateUser(userData=userData, userId=userId, dbConnect=dbConnect)

        return userData
    except Exception as e:

        logger.error(e)
        raise e