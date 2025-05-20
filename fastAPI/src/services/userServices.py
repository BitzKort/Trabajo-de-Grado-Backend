
from loguru import logger
from fastapi import HTTPException, status, Depends
from datetime import timedelta, datetime, date
from src.schemas.userSchema import UserInfoResponse, UserInfoEntry, UserUpdateModel
from src.schemas.nplSchemas import CompareRouterResponse
from src.repository.userRepository import getUserInfo, userUpdate
from src.repository.streakRepository import update_strike, update_exp_and_day
from src.repository.db import get_postgres
from src.services.authServices import get_current_user
from src.schemas.lessonSchemas import SaveLessonEnrtry

async def userInfo(userData: UserInfoEntry = Depends(), token:str = Depends(get_current_user), dbConnect = Depends(get_postgres)) -> UserInfoResponse:


    userInfoResult = await getUserInfo(userData.id, dbConnect)

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

async def updateUser(userData: UserUpdateModel = Depends(), token = Depends(get_current_user), dbConnect = Depends(get_postgres)):

    try:
        await userUpdate(userData, dbConnect)

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
        await update_exp_and_day(userData.userId, userData.newExp, newLastTime, dbConnect)

        
    
    except HTTPException:
        raise

    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    

    
