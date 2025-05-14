from fastapi import APIRouter, HTTPException, Query, Depends
from loguru import logger

from src.schemas.nplSchemas import QuestionCardResponse, SentenceCompareResponse
from src.services.nplServices import compareAnswer
from src.services.authServices import get_current_user
from typing import List,Annotated


nplRouter = APIRouter()

#investigar el envio con post, el uso de get va por paramss
@nplRouter.get("/compare", response_model=SentenceCompareResponse)

async def sentenceCompare(sentenceNlp: Annotated[str, Query(...)], token:str = Depends(get_current_user))-> SentenceCompareResponse:

    print(sentenceNlp)
    
    response = await compareAnswer(sentenceNlp)

    return response