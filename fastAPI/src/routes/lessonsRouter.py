
import asyncpg
import redis.asyncio as asyncredis
from fastapi import Depends, HTTPException, APIRouter, status
from loguru import logger
from src.repository.db import get_postgres, get_redis
from src.services.authServices import get_current_user
from src.services.lessonServices import verify_all_valid_lessons, verify_valid_lesson, get_redis_data
from src.schemas.lessonSchemas import VerifyAVLResponse, VerifyVLResponse, LessonWithQuestions, IncorrectQuestionResponse, AVLResponse, ListLessonWQ



lessonsRouter = APIRouter()

@lessonsRouter.get("/lessons")
async def lessonId( lessonData: VerifyVLResponse = Depends(verify_valid_lesson), db: asyncpg = Depends(get_postgres)) -> ListLessonWQ:
    

    """
        Ruta para obtener una leccion

        Retorna
        -------
        Objeto ListLessonWQ que contiene toda la informacion de la leccion (ids, preguntas y respuestas)

        Excepciones
        -------
        - Excepciones de conexión a la base de datos.
    """


    try:
        if not lessonData.status =="success":

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=lessonData.msg)
        
        
        lessonSplit = lessonData.lessonId.split(":")

        _, lessonPostgresId = lessonSplit
        query =query = "SELECT l.id AS lesson_id, l.title, l.text, q.id AS question_id, q.question_text, q.answer, q.distractor FROM lessons l JOIN questions q ON q.lesson_id = l.id WHERE l.id = $1;"

        questionList =[]

        async with db.acquire() as conn:

            questionsData = await conn.fetch(query, lessonPostgresId)

            for question in questionsData:
                formatedQuestion = LessonWithQuestions(**dict(question))
                questionList.append(formatedQuestion)
            
            print(ListLessonWQ(questions=questionList))
            return ListLessonWQ(questions=questionList)
    except Exception as e:

        logger.error(e)
        raise e


@lessonsRouter.get("/AllLessons")
async def get_lesson_keys(lessonData: VerifyAVLResponse = Depends(verify_all_valid_lessons), redisConnect: asyncredis.Redis = Depends(get_redis)) -> AVLResponse:



    """
        Ruta para obtener la información general de todas las lecciones pendientes por realizar.
        Esta ruta se conecta a la base de datos de redis.
        
        Retorna
        -------
        Objeto AVLResponse que contiene la informacion general de las lecciones pendientes 

        Excepciones
        -------
        - Excepciones dentro de los metodos de servicio.
    """

    try:

        if lessonData.status =="success":

            questionList = await get_redis_data(redisConnect, lessonData.pending_lessons)

            return AVLResponse(status=lessonData.status, pending_lessons=questionList, total_pending=lessonData.total_pending)


    except Exception as e:

        logger.error(e)
        raise e


@lessonsRouter.get("/failedQuestions")
async def get_failed_questions(dbConnect: asyncpg.pool = Depends(get_postgres), userId: str = Depends(get_current_user)) -> IncorrectQuestionResponse:

    """
        Ruta para obtener las preguntas incorrectas por el usuario.
        
        NOTA
        -------
        Esta ruta retorna una pregunta incorrecta de forma aleatoria de la tabla.

        Retorna
        -------
        Objeto IncorrectQuestionResponse que da la información de la pregunta incorrecta.

        Excepciones
        -------
        - 200 ok: No tienes preguntas incorrectas.
        - Excepciones dentro de los metodos de servicio.
    """


    query = """SELECT l.id AS lesson_id, q.id AS question_id, l.title, l.text, q.question_text,
                q.answer, q.distractor FROM lessons AS l JOIN questions AS q ON q.lesson_id = l.id
                JOIN registration_questions AS rq ON rq.question_id = q.id WHERE rq.is_correct = FALSE
                AND rq.user_id = $1 ORDER BY RANDOM() LIMIT 1;
            """
    try:

        async with dbConnect.acquire() as conn:

            results = await conn.fetchrow(query, userId)

            if not results:

                raise HTTPException(status_code=status.HTTP_200_OK, detail="No tienes preguntas incorrectas.")
            
            
            return IncorrectQuestionResponse(**dict(results))
    
    except Exception as e:

        logger.error(e)
        raise e

