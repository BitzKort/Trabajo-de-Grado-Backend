from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
import redis.asyncio as asyncredis
from src.schemas.nplSchemas import SentenceCompareResponse, CompareRouterResponse
from src.services.nplServices import compareAnswer
from src.services.userServices import updateExp, saveRedisLesson
from src.services.authServices import get_current_user
from src.schemas.lessonSchemas import SaveLessonEnrtry
from src.schemas.nplSchemas import SentencesCompareEnrty
from src.repository.db import get_postgres, get_redis
from src.repository.userRepository import deleteFromIncorrect, insertIntoIncorrect
from datetime import datetime


nplRouter = APIRouter()

@nplRouter.post("/compareResponses", response_model=CompareRouterResponse)
async def sentenceCompare(userCompareData: SentencesCompareEnrty , userId: str = Depends(get_current_user), redisConnect:asyncredis.Redis = Depends(get_redis), dbConnect = Depends(get_postgres))-> CompareRouterResponse:

    try:

        userData = await compareAnswer(userCompareData=userCompareData, userId=userId)

        newLastTime = datetime.today()

        newExp = userData.newExp

        if float(userData.score) >= 0.7:

            await updateExp(userData.userId, newExp, newLastTime, dbConnect)

            await saveRedisLesson(userData.userId, userData.lesson_id, redisConnect)
            
            if userData.type == 2:
            
                await deleteFromIncorrect(userData.userId, userData.question_id, dbConnect)

            return  CompareRouterResponse(status="success", userId=userData.userId, score=userData.score, msg="Respuesta Correcta")

        else:


            await saveRedisLesson(userData.userId, userData.lesson_id, redisConnect)

            if userData.type == 1:

                await insertIntoIncorrect(userData.userId,userData.question_id, dbConnect)
            

            return CompareRouterResponse(status="failed", userId=userData.userId, score=userData.score, msg="Respuesta Incorrecta")
        
    except Exception as e:

        logger.error(e)

        raise e
