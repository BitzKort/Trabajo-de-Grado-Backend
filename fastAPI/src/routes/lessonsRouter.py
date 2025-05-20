
import asyncpg
import redis.asyncio as asyncredis
from fastapi import Depends, HTTPException, APIRouter, Query, status
from loguru import logger
from src.repository.db import get_postgres, get_redis
from src.services.authServices import get_current_user
from src.services.lessonServices import verify_all_valid_lessons, verify_valid_lesson, get_redis_data
from src.schemas.lessonSchemas import VerifyAVLResponse, VerifyVLResponse, LessonWithQuestions, IncorrectQuestionResponse, AVLResponse, ListLessonWQ

from typing import Annotated


lessonsRouter = APIRouter()

#Router para traer la leccion con preguntas
@lessonsRouter.get("/lessons")
async def lessonId( lessonData: VerifyVLResponse = Depends(verify_valid_lesson), db: asyncpg = Depends(get_postgres)) -> ListLessonWQ:

    try:
        if not lessonData.status =="success":

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=lessonData.msg)
        
        
        lessonSplit = lessonData.lessonId.split(":")

        _, lessonPostgresId = lessonSplit
        query ="SELECT l.id, l.title, l.text, q.id AS question_id, q.question_text, q.answer, q.distractor FROM lessons l CROSS JOIN jsonb_array_elements_text(l.questions_id) AS p(id) JOIN questions q ON q.id = p.id::text WHERE l.id = $1;"

        questionList =[]

        async with db.acquire() as conn:

            questionsData = await conn.fetch(query, lessonPostgresId)

            for question in questionsData:
                logger.info(question)
                formatedQuestion = LessonWithQuestions(**dict(question))
                questionList.append(formatedQuestion)
            
            return ListLessonWQ(questions=questionList)
    except Exception as e:

        logger.error(e)
        raise e



#cambiar y hacer verificacion con neon de si un usuario es apto o no
@lessonsRouter.get("/AllLessons")
async def get_lesson_keys(lessonData: VerifyAVLResponse = Depends(verify_all_valid_lessons), redisConnect: asyncredis.Redis = Depends(get_redis), token:str = Depends(get_current_user)) -> AVLResponse:

    try:

        if lessonData.status =="success":

            questionList = await get_redis_data(redisConnect, lessonData.pending_lessons)

            return AVLResponse(status=lessonData.status, pending_lessons=questionList, total_pending=lessonData.total_pending)


    except Exception as e:

        logger.error(e)
        raise e


@lessonsRouter.get("/failedQuestions")
async def get_failed_questions( userId: str, dbConnect: asyncpg.pool = Depends(get_postgres), token: str = Depends(get_current_user)) -> IncorrectQuestionResponse:

    
    query = """SELECT l.id, l.title, l.text, q.question_text, q.answer, q.distractor FROM incorrect_questions iq
                JOIN questions q ON iq.question_id = q.id JOIN lessons l ON EXISTS ( SELECT 1 FROM 
                jsonb_array_elements_text(l.questions_id) AS elem WHERE elem = q.id)
                WHERE iq.user_id = $1 ORDER BY RANDOM() LIMIT 1;
"""


    try:

        async with dbConnect.acquire() as conn:

            results = await conn.fetch(query, userId)

            if not results:

                logger.warning("El usuario no tiene preguntas incorrectas.")

                raise HTTPException(status_code=status.HTTP_200_OK, detail="El usuario no tiene preguntas incorrectas.")
            
            
            return IncorrectQuestionResponse(**dict(results))
    
    except Exception as e:

        logger.error(e)
        raise e

