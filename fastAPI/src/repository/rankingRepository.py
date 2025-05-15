from fastapi import HTTPException, status
from loguru import logger
import asyncpg
from src.schemas.rankingSchemas import RankingResponse
from typing import List


async def getRanking(dbConnect: asyncpg.pool) -> List[RankingResponse]:

    query =" SELECT u.username, r.exp, r.dias FROM racha r INNER JOIN users u ON r.id = u.id ORDER BY r.exp DESC LIMIT 10;"

    try:

        async with dbConnect.acquire() as conn:

            players = await conn.fetch(query)

            if players:

                return [ RankingResponse(**dict(player)) for player in players]
        
    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)