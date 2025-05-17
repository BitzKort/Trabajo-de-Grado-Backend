
from loguru import logger
from fastapi import HTTPException, status, Depends
from datetime import timedelta, datetime, date
from src.schemas.userSchema import UserInfoResponse, UserInfoEntry, UserUpdateModel
from src.schemas.nplSchemas import CompareRouterResponse
from src.repository.userRepository import getUserInfo, userUpdate
from src.repository.streakRepository import update_strike, update_exp
from src.repository.db import get_postgres
from src.services.authServices import get_current_user

async def userInfo(userData: UserInfoEntry = Depends(), token:str = Depends(get_current_user), dbConnect = Depends(get_postgres)) -> UserInfoResponse:


    userInfoResult = await getUserInfo(userData.id, dbConnect)

    if not userInfoResult:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something happend getting the user info")

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

        return {"msg":"user updated succesfully"}
    
    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    


async def updateExp(userId, newExp, newLastTime, score, dbConnect):

    try:
        await update_exp(userId, newExp, newLastTime, dbConnect)

        return CompareRouterResponse(userId=userId, score=score, msg="Respuesta correcta")
    
    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    


    
