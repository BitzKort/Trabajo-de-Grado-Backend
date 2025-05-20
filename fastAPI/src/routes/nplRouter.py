from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from src.schemas.nplSchemas import SentenceCompareResponse, CompareRouterResponse
from src.services.nplServices import compareAnswer
from src.services.userServices import updateExp
from src.schemas.lessonSchemas import SaveLessonEnrtry
from src.repository.db import get_postgres
from src.repository.userRepository import deleteFromIncorrect, insertIntoIncorrect
from datetime import datetime


nplRouter = APIRouter()

@nplRouter.post("/compareResponses", response_model=CompareRouterResponse)
async def sentenceCompare(userData:SentenceCompareResponse = Depends(compareAnswer), dbConnect = Depends(get_postgres))-> CompareRouterResponse:

    try:

        newLastTime = datetime.today()

        newExp = userData.newExp

        if userData.score >= 0.7:

            await updateExp(userData.userId, newExp, newLastTime, dbConnect)
            
            if userData.type =="second":
            
                await deleteFromIncorrect(userData.userId,userData.question_id, dbConnect)

            return  CompareRouterResponse(userId=userData.userId, score=userData.score, msg="Respuesta Correcta")

        else:

            await insertIntoIncorrect(userData.userId,userData.question_id, dbConnect)

            return CompareRouterResponse(userId=userData.userId, score=userData.score, msg="Respuesta Incorrecta")
        
    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
