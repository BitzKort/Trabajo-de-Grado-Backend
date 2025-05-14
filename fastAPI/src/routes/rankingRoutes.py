from fastapi import Depends, APIRouter
from src.schemas.userSchema import RankingResponse
from typing import List
import asyncpg
from src.repository.db import get_postgres
from src.services.authServices import get_current_user
from loguru import logger

rankingRouter = APIRouter()

@rankingRouter.get("/ranking", response_model=List[RankingResponse])

async def getRanking(dbConect: asyncpg.Pool = Depends(get_postgres), token:str = Depends(get_current_user)) -> List[RankingResponse]:

    query =" SELECT u.username, r.exp, r.dias FROM racha r INNER JOIN users u ON r.id = u.id ORDER BY r.exp DESC LIMIT 10;"


    try:

        async with dbConect.acquire() as conn:

            players = await conn.fetch(query)

            if players:

                logger.success("ranking was given well")

                return [ RankingResponse(**dict(player)) for player in players]
        
    except Exception as e:

        logger.error(f"something happend on ranking: {e}")