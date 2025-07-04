import os
from fastapi import HTTPException, status
from src.schemas.nplSchemas import SentencesCompareEnrty, SentenceCompareResponse
from sentence_transformers import CrossEncoder
from loguru import logger

stsb_path = os.getenv("STSB_MODEL_PATH")


async def compareAnswer(userCompareData:SentencesCompareEnrty, userId: str ) -> SentenceCompareResponse:


    """
        Método para comparar la respuesta del usuario con la del modelo.
    
        Retorna
        -------
        Objeto SentenceCompareResponse informacion general de la prediccion.

        Excepciones
        -------
        - Excepciones del modelo.
    """

    try:

        stsb_model = CrossEncoder(model_name=stsb_path)

        predict = str(stsb_model.predict((userCompareData.sentenceNlp, userCompareData.sentenceUser)))
        
        return SentenceCompareResponse(userId=userId, newExp= userCompareData.newExp, lesson_id=userCompareData.lesson_id, question_id=userCompareData.question_id, score=predict, type=userCompareData.type)
    
    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

