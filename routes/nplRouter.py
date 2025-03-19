from fastapi import APIRouter, HTTPException
from loguru import logger

from schemas.nplSchemas import Something
from services.nplServices import getText

nplRouter = APIRouter()


@nplRouter.get("/getQuestionCard", response_model=Something)


async def TextForNow() -> Something:

    response = await getText()

    return response