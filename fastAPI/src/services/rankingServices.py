from fastapi import Depends, HTTPException, status
from loguru import logger
from typing import List
from src.repository.rankingRepository import getRanking
from src.services.authServices import get_current_user
from src.repository.db import get_postgres
from src.schemas.rankingSchemas import RankingResponse


async def ranking(dbConnect = Depends(get_postgres), userId = Depends(get_current_user)) -> List[RankingResponse]:
    
    try:
        ranking = await getRanking(dbConnect)

        if not ranking:

            logger.error("Error retornando el ranking.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retornando el ranking.")
        
        return ranking
    
    except Exception as e:

        raise e