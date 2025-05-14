import os
from src.schemas.nplSchemas import QuestionCardResponse, SentenceCompareResponse
from sentence_transformers import CrossEncoder
from loguru import logger
import re
import dotenv

stsb_path = os.getenv("STSB_MODEL_PATH")


async def compareAnswer(SentenceNlp) -> SentenceCompareResponse:

    stsb_model = CrossEncoder(model_name=stsb_path)

    predict = str(stsb_model.predict((SentenceNlp, "hi, how are you")))
    
    return SentenceCompareResponse(sentenceNlp=SentenceNlp, sentenceUser= "hi, how are you", score=predict)

