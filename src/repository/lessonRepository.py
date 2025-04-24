from fastapi import HTTPException
from tsidpy import TSID
from loguru import logger

async def insertLessons(userData, dbconect):

    id = str(TSID.create())

    query ="INSERT INTO lessons (id, title, text, questions) VALUES (($1)::text, $2, $3, $4, $5);"


    try: 
        async with dbconect.acquire() as conn:

            await conn.fetchrow(
                query,
                id,
                userData.name,
                userData.username,
                userData.email,
                userData.password
            )

            logger.success("usuario creado exitosamente")

            return {"msg": "usuario creado exitosamente"}
    
    