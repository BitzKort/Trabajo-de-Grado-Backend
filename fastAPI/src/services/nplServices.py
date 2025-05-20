import os
from fastapi import Depends, HTTPException, status
from src.schemas.nplSchemas import SentencesCompareEnrty, SentenceCompareResponse
from sentence_transformers import CrossEncoder
from src.services.authServices import get_current_user
from loguru import logger

stsb_path = os.getenv("STSB_MODEL_PATH")


async def compareAnswer(userCompareData:SentencesCompareEnrty = Depends(), userId: str = Depends(get_current_user)) -> SentenceCompareResponse:

    try:

        stsb_model = CrossEncoder(model_name=stsb_path)

        predict = str(stsb_model.predict((userCompareData.sentenceNlp, userCompareData.sentenceUser)))
        
        return SentenceCompareResponse(userId=userId, newExp= userCompareData.newExp, lesson_id=userCompareData.lesson_id, score=predict, type=userCompareData.type)
    
    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

