from fastapi import Depends, HTTPException, APIRouter, Query
from loguru import logger
from src.schemas.userSchema import Lessons, LessonResponse
import asyncpg
from src.repository.db import get_postgres
from typing import Annotated


lessonsRouter = APIRouter()

#Router para traer todas las lecciones
@lessonsRouter.get("/lessons")
async def getAllLessons(db: asyncpg = Depends(get_postgres)):

    query =" SELECT id, title, questions FROM lessons;"

    async with db.acquire() as conn:

        lessons = await conn.fetch(query)

        return [ Lessons(**dict(lesson)) for lesson in lessons]
    
#Router para traer  leccion especifica

@lessonsRouter.get("/lesson", response_model=LessonResponse)

async def lessonId(id:Annotated[str, Query(...)], db: asyncpg = Depends(get_postgres)) -> LessonResponse:

    query = "SELECT * FROM lessons WHERE id = $1;"

    try:

        async with db.acquire() as conn:

            response = await conn.fetchrow(query, id)

            return LessonResponse(**dict(response))
    except Exception as e:

        logger.error("something happend: {}".format(e))




#Router para la actualizacion de todas las lecciones
@lessonsRouter.get("/UpdateLessons")

async def getAllLessons(db: asyncpg = Depends(get_postgres)):

    query =" SELECT id, title, questions FROM lessons;"

    async with db.acquire() as conn:

        lessons = await conn.fetch(query)

        return [ Lessons(**dict(lesson)) for lesson in lessons]