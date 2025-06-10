from fastapi import APIRouter, Depends
from loguru import logger
import redis.asyncio as asyncredis
from src.schemas.nplSchemas import  CompareRouterResponse
from src.services.nplServices import compareAnswer
from src.services.userServices import updateExp, saveRedisLesson
from src.services.authServices import get_current_user
from src.schemas.nplSchemas import SentencesCompareEnrty
from src.repository.db import get_postgres, get_redis
from src.repository.userRepository import save_on_registration_questions, save_solved_lessons, update_on_registration_questions
from datetime import datetime


nplRouter = APIRouter()

@nplRouter.post("/compareResponses", response_model=CompareRouterResponse)
async def sentenceCompare(userCompareData: SentencesCompareEnrty , userId: str = Depends(get_current_user), redisConnect:asyncredis.Redis = Depends(get_redis), dbConnect = Depends(get_postgres))-> CompareRouterResponse:


    """
        Ruta para comparar las respuesta del usuario con la de modelo.

        Retorna
        -------
        Objeto CompareRouterResponse que contiene el puntaje obtenido e información adicional.

        Excepciones
        -------
        - Excepciones dentro de los metodos de servicio.
    """

    try:
        lesson_id = userCompareData.lesson_id
        userData = await compareAnswer(userCompareData=userCompareData, userId=userId)
        newLastTime = datetime.today()

        newExp = userData.newExp

        if float(userData.score) >= 0.7:

            await updateExp(userData.userId, newExp, newLastTime, dbConnect)

            await saveRedisLesson(userData.userId, userData.lesson_id, redisConnect)

            if userData.type == 1:

                if userCompareData.question_number == 0:
                    
                    await save_solved_lessons(userData.userId, lesson_id, dbConnect)
    
                await save_on_registration_questions(userData.userId,userData.question_id, True, dbConnect)
            
            elif userData.type == 2:

                await update_on_registration_questions(userData.userId,userData.question_id, True, dbConnect)

            return  CompareRouterResponse(status="success", userId=userData.userId, score=userData.score, msg="Respuesta Correcta")

        else:

            await saveRedisLesson(userData.userId, userData.lesson_id, redisConnect)



            if userData.type == 1:

                if userCompareData.question_number == 0:
                    await save_solved_lessons(userData.userId, lesson_id, dbConnect)
                await save_on_registration_questions(userData.userId,userData.question_id, False, dbConnect)
            

            return CompareRouterResponse(status="failed", userId=userData.userId, score=userData.score, msg="Respuesta Incorrecta")
        
    except Exception as e:

        logger.error(e)

        raise e
