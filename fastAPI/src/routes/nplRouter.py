from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from src.schemas.nplSchemas import QuestionCardResponse, SentenceCompareResponse
from src.services.nplServices import getText, getQuestionRACE, getQuestionSQUAD, compareAnswer
from typing import List,Annotated


nplRouter = APIRouter()

#investigar el envio con post, el uso de get va por paramss
@nplRouter.get("/compare", response_model=SentenceCompareResponse)

async def sentenceCompare(sentenceNlp: Annotated[str, Query(...)])-> SentenceCompareResponse:

    print(sentenceNlp)
    
    response = await compareAnswer(sentenceNlp)

    return response