
from loguru import logger
from fastapi import HTTPException, status, Depends
from datetime import date, timedelta
from src.schemas.userSchema import UserInfoResponse, UserInfoEntry
from src.repository.userRepository import getUserName, getUserInfo, update_strike
from src.repository.db import get_postgres
from src.services.authServices import get_current_user

async def userInfo(userData: UserInfoEntry = Depends(), token:str = Depends(get_current_user), dbConnect = Depends(get_postgres)) -> UserInfoResponse:


    userInfoResult = await getUserInfo(userData.id, dbConnect)

    if not userInfoResult:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something happend getting the user info")

    else:

        return userInfoResult, dbConnect
    

async def verify_streak(userInfo, dbConnect ):

    today = date.today()
    if not userInfo.last_activity_date == today:
        #si no es hoy es pq falta por hacer al menos una leccion

        # si no es hoy y no tiene tiempo de 1 dia, se reinicia
        if not userInfo.last_activity_date == today - timedelta(days=1):

            userInfo.streak_count = 1
            userInfo.last_activity_date = today

            await update_strike(userInfo, dbConnect)
    
    return userInfo

    
