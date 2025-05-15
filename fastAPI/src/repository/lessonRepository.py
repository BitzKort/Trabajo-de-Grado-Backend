from fastapi import HTTPException
from tsidpy import TSID
from loguru import logger




#Esto es utilizando redis y no es para insert, sera para select
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

            logger.success("Leccion guardada en neon")

    except Exception as e:

        logger.error(f"leccion no guardada en neon por {e}")
