from fastapi import APIRouter, HTTPException, Query, Depends
from loguru import logger
from src.schemas.nplSchemas import SentenceCompareResponse, SentencesCompareEnrty
from src.services.nplServices import compareAnswer
from typing import Annotated

nplRouter = APIRouter()


@nplRouter.get("/compareResponses", response_model=SentenceCompareResponse)
async def sentenceCompare(sentenceNlp: Annotated[SentencesCompareEnrty, Query(...)], compareResponse = Depends(compareAnswer))-> SentenceCompareResponse:

    return compareResponse