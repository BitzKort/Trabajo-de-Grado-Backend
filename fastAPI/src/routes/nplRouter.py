from fastapi import APIRouter, HTTPException, Query, Depends
from loguru import logger
from src.schemas.nplSchemas import SentenceCompareResponse, CompareRouterResponse
from src.services.nplServices import compareAnswer
from src.services.userServices import updateExp
from src.repository.db import get_postgres
from typing import Annotated
from datetime import datetime
nplRouter = APIRouter()


@nplRouter.post("/compareResponses", response_model=CompareRouterResponse)
async def sentenceCompare(userData:SentenceCompareResponse = Depends(compareAnswer), dbConnect = Depends(get_postgres))-> CompareRouterResponse:

    
    if userData.score >= 0.7:

        newLastTime = datetime.today()

        newExp = userData.newExp

        try:

            response = await updateExp(userData.userId, newExp, newLastTime, userData.score, dbConnect)

            return response

        except Exception:

            raise

    else:
        return CompareRouterResponse(userId=userData.userId, score=userData.score, msg="Respuesta Incorrecta")

