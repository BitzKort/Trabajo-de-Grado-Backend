import redis
import asyncpg
from fastapi import Depends, HTTPException, APIRouter, Query, status
from loguru import logger
from src.schemas.userSchema import Lessons, LessonResponse
from src.repository.db import get_postgres, get_redis
from src.services.authServices import get_current_user
from src.services.lessonServices import verify_all_valid_lessons, verify_valid_lesson
from src.schemas.lessonSchemas import VerifyAVLResponse, VerifyVLResponse

from typing import Annotated


lessonsRouter = APIRouter()

#Router para traer la leccion con preguntas
@lessonsRouter.get("/lessons")
async def lessonId( lessonData: VerifyVLResponse = Depends(verify_valid_lesson), db: asyncpg = Depends(get_postgres)) -> LessonResponse:


    if not lessonData.status =="success":

        raise HTTPException(status_code=status.WS_1003_UNSUPPORTED_DATA, detail={lessonData.status, lessonData.msg})
    
    
    query = "SELECT * FROM lessons WHERE id = $1;"

    try:

        async with db.acquire() as conn:

            response = await conn.fetchrow(query, id)

            return LessonResponse(**dict(response))
    except Exception as e:

        logger.error("something happend: {}".format(e))
        raise e



#cambiar y hacer verificacion con neon de si un usuario es apto o no
@lessonsRouter.get("/AllLessons")
async def get_lesson_keys( lessonData: VerifyAVLResponse = Depends(verify_all_valid_lessons), token:str = Depends(get_current_user)) -> VerifyAVLResponse:

    try:

        return lessonData

    except Exception as e:

        raise e


@lessonsRouter.get("/failedQuestions")

async def get_failed_questions():

    pass
