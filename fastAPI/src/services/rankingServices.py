from fastapi import Depends, HTTPException, status
from loguru import logger
from src.repository.rankingRepository import getRanking
from src.services.authServices import get_current_user
from src.repository.db import get_postgres
from src.schemas.rankingSchemas import RankingResponse
from typing import List

async def ranking(dbConnect = Depends(get_postgres), token = Depends(get_current_user)) -> List[RankingResponse]:

    ranking = await getRanking(dbConnect)

    if not ranking:

        logger.error("something happend giving the ranking")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="something happend giving the ranking")
    
    return ranking