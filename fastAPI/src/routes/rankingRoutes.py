from fastapi import Depends, APIRouter
from src.schemas.rankingSchemas import RankingResponse
from typing import List
import asyncpg
from loguru import logger
from src.services.rankingServices import ranking

rankingRouter = APIRouter()

@rankingRouter.get("/ranking", response_model=List[RankingResponse])
async def get_ranking(ranking: List[RankingResponse] = Depends(ranking)) -> List[RankingResponse]:

    return ranking