from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from src.schemas.nplSchemas import SentenceCompareResponse, CompareRouterResponse
from src.services.nplServices import compareAnswer
from src.services.userServices import updateExp
from src.schemas.lessonSchemas import SaveLessonEnrtry
from src.repository.db import get_postgres
from datetime import datetime


nplRouter = APIRouter()

@nplRouter.post("/compareResponses", response_model=CompareRouterResponse)
async def sentenceCompare(userData:SentenceCompareResponse = Depends(compareAnswer), dbConnect = Depends(get_postgres))-> CompareRouterResponse:

    try:

        if userData.score >= 0.7:

            return  CompareRouterResponse(userId=userData.userId, score=userData.score, msg="Respuesta Correcta")

        else:
            return CompareRouterResponse(userId=userData.userId, score=userData.score, msg="Respuesta Incorrecta")
        
    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

@nplRouter.post("/saveLesson", response_model=CompareRouterResponse)
async def sentenceCompare(userData:SaveLessonEnrtry = Depends(updateExp), dbConnect = Depends(get_postgres))-> CompareRouterResponse:

    
    newLastTime = datetime.today()

    newExp = userData.newExp

    try:

        await updateExp(userData.userId, newExp, newLastTime, dbConnect)

        await saveLessonCompleted(userData.userId, userData.lessonId, dbConnect)


    except Exception as e:

        logger.error(e)
        
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)