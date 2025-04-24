from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from schemas.nplSchemas import QuestionCardResponse, SentenceCompareResponse
from services.nplServices import getText, getQuestionRACE, getQuestionSQUAD, compareAnswer
from typing import List,Annotated




nplRouter = APIRouter()

@nplRouter.get("/getQuestionCard", response_model=List[QuestionCardResponse])


async def QuestionGenerator() -> List[QuestionCardResponse]:

    text = await getText()

    questionRaceCard = await getQuestionRACE(text)

    questionSquadCard = await getQuestionSQUAD(text)


    return [questionRaceCard, questionSquadCard]


#investigar el envio con post, el uso de get va por paramss
@nplRouter.get("/compare", response_model=SentenceCompareResponse)

async def sentenceCompare(sentenceNlp: Annotated[str, Query(...)])-> SentenceCompareResponse:

    print(sentenceNlp)
    
    response = await compareAnswer(sentenceNlp)

    return response