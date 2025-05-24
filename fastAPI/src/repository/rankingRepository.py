import asyncpg
from fastapi import HTTPException, status
from loguru import logger
from typing import List
from src.schemas.rankingSchemas import RankingResponse


async def getRanking(dbConnect: asyncpg.pool) -> List[RankingResponse]:

    query =" SELECT u.username, r.exp, r.days FROM streaks r INNER JOIN users u ON r.id = u.id WHERE r.exp > 0 ORDER BY r.exp DESC LIMIT 10;"

    try:

        async with dbConnect.acquire() as conn:

            players = await conn.fetch(query)

            if players:

                return [ RankingResponse(**dict(player)) for player in players]
        
    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)