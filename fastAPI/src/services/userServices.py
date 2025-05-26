import redis.asyncio as asyncredis
import asyncpg
from loguru import logger
from fastapi import HTTPException, status, Depends
from datetime import timedelta, datetime
from src.schemas.userSchema import UserInfoResponse, UserUpdateModel
from src.repository.userRepository import getUserInfo, userUpdate
from src.repository.streakRepository import update_strike, update_exp, get_last_activity_date, update_days
from src.repository.db import get_postgres
from src.services.authServices import get_current_user


async def userInfo(userId :str = Depends(get_current_user), dbConnect = Depends(get_postgres)) -> UserInfoResponse:

    """
        Método de logica para obtener la información general del usuario.
    
        Retorna
        -------
        Objeto UserInfoResponse

        Excepciones
        -------
        - Excepciones dentro de los metodos del repositorio.
    """


    userInfoResult = await getUserInfo(userId, dbConnect)

    if not userInfoResult:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retornando la informacion del usuario")

    else:

        return userInfoResult, dbConnect
    

async def verify_streak(userInfo, dbConnect):


    """
        Método de logica para verificar la racha del usuario.
    
        Retorna
        -------
        Objeto Streak

        Excepciones
        -------
        - Excepciones dentro de los metodos del repositorio.
    """

    try:
        today = datetime.today()
        if not userInfo.last_activity_date.date() == today.date():

            if userInfo.last_activity_date < today - timedelta(days=1):

                userInfo.days = 0
                userInfo.last_activity_date = today

                userInfo = await update_strike(userInfo, dbConnect)
        
        return userInfo
    
    except Exception as e:

        raise e

async def updateUser(userData: UserUpdateModel, userId: str, dbConnect: asyncpg.pool):

    """
        Método de logica para actualizar el name o el username del usuario.
    
        Retorna
        -------
        Objeto json con msg: Usuario actualizado exitosamente.

        Excepciones
        -------
        - Excepciones dentro de los metodos del repositorio.
    """

    try:
        await userUpdate(userData, userId, dbConnect)

        return {"msg":"Usuario actualizado exitosamente."}
    
    except HTTPException:
        raise

    except Exception as e:

        logger.error(e)

        raise e
    

async def is_consecutive_day(last_activity: datetime) -> bool:


    """
        Método de logica para verificar si ya paso un dia desde la utima pregunta realizada por el usuario.
    
        Retorna
        -------
        Boolean: True si ya paso mas de un dia, False si no.

        Excepciones
        -------
        - Excepciones dentro de los metodos del repositorio.
    """
    

    now = datetime.now()
    
    if now - last_activity > timedelta(hours=24):
        return False

    yesterday = (now.date() - timedelta(days=1))
    return last_activity.date() == yesterday


async def updateExp(userId: str, newExp:str, newLastTime, dbConnect):

    """
        Método de logica para actualizar los puntos de experiencia del usuario.
    
        Retorna
        -------
        None

        Excepciones
        -------
        - Excepciones dentro de los metodos del repositorio.
    """


    try:

        old_last_time = await get_last_activity_date(userId, dbConnect)

        #si es un dia valido para que aumente el dia en la racha
        if await is_consecutive_day(old_last_time.last_activity_date):

            await update_days(userId, dbConnect)

        await update_exp(userId, newExp, newLastTime, dbConnect)  
    
    except HTTPException:
        raise

    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    


async def saveRedisLesson(user_id: str, lesson_id: str, redis:asyncredis.Redis) -> bool:
    """
    Método que añade la leccion al set de lecciones/completados del usuario.
    - Si la clave no existe, Redis la crea automáticamente al hacer SADD.

    Retorna
    -------
    - None

    Excepciones
    -------
    - Excepciones dentro de redis.
    """

    try: 
        user_key = f"user:{user_id}:completed"

        added = await redis.sadd(user_key, lesson_id)

    except Exception as e:

        logger.error(e)

        raise e
