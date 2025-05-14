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
async def getAllLessons(redis_client_pool: redis = Depends(get_redis), token:str = Depends(get_current_user) ):

    try:
        value = await redis_client_pool.get("lessons:default")
    except Exception as e:
        raise HTTPException(502, f"Error comunicándose con Redis: {e}")
    if value is None:
        raise HTTPException(404, "Clave no encontrada")
    return {"lessons_default": value}


#Este es para tener un crud para postgres
@lessonsRouter.get("/lesson", response_model=LessonResponse, )

async def lessonId(id:Annotated[str, Query(...)], db: asyncpg = Depends(get_postgres), token:str = Depends(get_current_user)) -> LessonResponse:

    query = "SELECT * FROM lessons WHERE id = $1;"

    try:

        async with db.acquire() as conn:

            response = await conn.fetchrow(query, id)

            return LessonResponse(**dict(response))
    except Exception as e:

        logger.error("something happend: {}".format(e))






#Router para guardar las lecciones completadas por el user
@lessonsRouter.get("/saveLesson")

async def getAllLessons(db: asyncpg = Depends(get_postgres)):

    query =" SELECT id, title, questions FROM lessons;"

    async with db.acquire() as conn:

        lessons = await conn.fetch(query)

        return [ Lessons(**dict(lesson)) for lesson in lessons]