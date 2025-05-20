from fastapi import Depends, APIRouter, HTTPException, status
from src.schemas.rankingSchemas import RankingResponse
from typing import List
from loguru import logger
from src.services.rankingServices import ranking

rankingRouter = APIRouter()

@rankingRouter.get("/ranking", response_model=List[RankingResponse])
async def get_ranking(ranking: List[RankingResponse] = Depends(ranking)) -> List[RankingResponse]:

    try:

        return ranking
    
    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
