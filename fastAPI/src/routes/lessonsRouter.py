import redis
import asyncpg
from fastapi import Depends, HTTPException, APIRouter, Query
from loguru import logger
from src.schemas.userSchema import Lessons, LessonResponse
from src.repository.db import get_postgres, get_redis
from src.services.authServices import get_current_user
from typing import Annotated


lessonsRouter = APIRouter()

#Router para traer todas las lecciones
@lessonsRouter.get("/lessons")
async def lessonId(id:Annotated[str, Query(...)], db: asyncpg = Depends(get_postgres)) -> LessonResponse:

    query = "SELECT * FROM lessons WHERE id = $1;"

    try:

        async with db.acquire() as conn:

            response = await conn.fetchrow(query, id)

            return LessonResponse(**dict(response))
    except Exception as e:

        logger.error("something happend: {}".format(e))



#cambiar y hacer verificacion con neon de si un usuario es apto o no
@lessonsRouter.get("/AllLessons")
async def get_lesson_keys(redis: redis = Depends(get_redis), token:str = Depends(get_current_user) ):
    lesson_keys = []
    cursor = '0'
    pattern = "all_lessons"
    
    while True:
        cursor, keys = await redis.scan(
            cursor=cursor,
            match=pattern,
            count=10  # Cantidad a traer por iteración
        )
        lesson_keys.extend(keys)
        
        # Detenemos si no hay más claves o ya tenemos 10
        if cursor == 0 or len(lesson_keys) >= 10:
            break
    
    # Limitar a máximo 10 claves y quitar posibles duplicados
    return list(dict.fromkeys(lesson_keys))[:10]