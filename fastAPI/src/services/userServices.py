
from loguru import logger
from fastapi import HTTPException, status, Depends
from datetime import timedelta, datetime, date
import redis.asyncio as asyncredis
from src.schemas.userSchema import UserInfoResponse, UserUpdateModel
from src.schemas.nplSchemas import CompareRouterResponse
from src.repository.userRepository import getUserInfo, userUpdate
from src.repository.streakRepository import update_strike, update_exp, get_last_activity_day, update_days
from src.repository.db import get_postgres
from src.services.authServices import get_current_user
from src.schemas.lessonSchemas import SaveLessonEnrtry

async def userInfo(userId :str = Depends(get_current_user), dbConnect = Depends(get_postgres)) -> UserInfoResponse:


    userInfoResult = await getUserInfo(userId, dbConnect)

    if not userInfoResult:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retornando la informacion del usuario")

    else:

        return userInfoResult, dbConnect
    

async def verify_streak(userInfo, dbConnect ):

    today = datetime.today()
    if not userInfo.last_activity_date.date() == today.date():
        #si no es hoy es pq falta por hacer al menos una leccion

        # si no es hoy y no tiene tiempo de 1 dia, se reinicia
        if userInfo.last_activity_date < today - timedelta(days=1):

            userInfo.dias = 1
            userInfo.last_activity_date = today

            userInfo = await update_strike(userInfo, dbConnect)
    
    return userInfo

async def updateUser(userData: UserUpdateModel = Depends(), userId = Depends(get_current_user), dbConnect = Depends(get_postgres)):

    try:
        await userUpdate(userData, userId, dbConnect)

        return {"msg":"Usuario actualizado exitosamente."}
    
    except HTTPException:
        raise

    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    

async def is_consecutive_day(last_activity: datetime) -> bool:
    now = datetime.now()
    
    # Verifica si ya pasaron más de 24 horas
    if now - last_activity > timedelta(hours=24):
        return False

    # Verifica si los días son consecutivos (ayer y hoy)
    yesterday = (now.date() - timedelta(days=1))
    return last_activity.date() == yesterday


async def updateExp(newLastTime, dbConnect, userData:SaveLessonEnrtry = Depends()):

    try:

        old_last_time = await get_last_activity_day(userData.userId, dbConnect)

        #si es un dia valido para que aumente el dia en la racha
        if await is_consecutive_day(old_last_time):

            await update_days(userData.userId, dbConnect)

        await update_exp(userData.userId, userData.newExp, newLastTime, dbConnect)


        
    
    except HTTPException:
        raise

    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    


async def saveRedisLesson(user_id: str, lesson_id: str, redis:asyncredis.Redis) -> bool:
    """
    Añade la leccion al set de lecciones/completados del usuario.
    - Si la clave no existe, Redis la crea automáticamente al hacer SADD.
    - Devuelve True si el item se añadió (no existía antes), False si ya estaba.
    """

    try: 
        user_key = f"user:{user_id}:completed"

        # 2) Añadir al set (crea la clave si no existe)
        added = await redis.sadd(user_key, lesson_id)
        # sadd devuelve 1 si el elemento NO estaba y se añade, 0 si ya existía
        if not added:

            logger.warning(f"{lesson_id} ya estaba en {user_key}; no hay duplicados.")

    except Exception as e:

        logger.error(e)

        raise e
