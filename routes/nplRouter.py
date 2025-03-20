from fastapi import APIRouter, HTTPException
from loguru import logger

from schemas.nplSchemas import QuestionCardResponse
from services.nplServices import getText, getQuestion

nplRouter = APIRouter()


@nplRouter.get("/getQuestionCard", response_model=QuestionCardResponse)


async def TextForNow() -> QuestionCardResponse:

    text = await getText()

    question = await getQuestion(text)


    return response