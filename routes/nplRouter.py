from fastapi import APIRouter, HTTPException
from loguru import logger

from schemas.nplSchemas import QuestionCardResponse
from services.nplServices import getText, getQuestion
from typing import List



nplRouter = APIRouter()

@nplRouter.get("/getQuestionCard", response_model=QuestionCardResponse)


async def QuestionGenerator() -> QuestionCardResponse:

    text = await getText()

    questionCard = await getQuestion(text)


    return questionCard