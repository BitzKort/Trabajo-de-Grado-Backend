import redis.asyncio as asyncredis
from fastapi import Depends, HTTPException, status
from typing import List
from loguru import logger
from src.services.userServices import get_current_user
from src.repository.db import get_redis
from src.schemas.lessonSchemas import VerifyAVLResponse, VerifyVLResponse, LessonIdentry, RedisLesson


async def verify_all_valid_lessons(redisConnect: asyncredis.Redis = Depends(get_redis), userId: str = Depends(get_current_user)) -> VerifyAVLResponse:
   
    """
        Método para verificar las lecciones por completar del usuario.
    
        Retorna
        -------
        Objeto VerifyAVLResponse que contiene la informacion general de las lecciones pendientes.

        Excepciones
        -------
        - Excepciones dentro de redis.
    """

    try:
        
        lessons_key ="all_lessons"
        
        if not await redisConnect.exists(lessons_key):

             return VerifyAVLResponse(status="success", pending_lessons=[], total_pending=0)
        

        all_lessons = await redisConnect.smembers(lessons_key)

        user_key = f"user:{userId}:completed"
        if not await redisConnect.exists(user_key):
        
            return VerifyAVLResponse(status="success", pending_lessons=list(all_lessons), total_pending=len(all_lessons))
        
       
        user_completed = await redisConnect.smembers(user_key)
        pending_lessons = list(set(all_lessons) - set(user_completed))
        
        return VerifyAVLResponse(status="success", pending_lessons=pending_lessons, total_pending=len(pending_lessons))
    
    except Exception as e:

        logger.error(e)
        raise e

async def verify_valid_lesson(redisConnect: asyncredis.Redis= Depends(get_redis), userData: LessonIdentry = Depends(), userId: str = Depends(get_current_user)) -> VerifyVLResponse:

    """
        Método para verificar si la leccion es valida para el usuario.
    
        Retorna
        -------
        Objeto VerifyVLResponse que contiene un status y un mensaje si la leccion esta disponible o no.

        Excepciones
        -------
        - Excepciones dentro de redis.
    """

    try:

        if not await redisConnect.exists("all_lessons"):

            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="nuevas lecciones se estan generandos")
        
        if not await redisConnect.sismember("all_lessons", userData.lessonId):
            return VerifyVLResponse(status="error", lessonId=userData.lessonId, msg="La leccion no existe")
        
        user_key = f"user:{userId}:completed"
        if not await redisConnect.exists(user_key):
            return VerifyVLResponse(status="success", lessonId=userData.lessonId, msg="Leccion disponible")
        
        if not await redisConnect.sismember(user_key, userData.lessonId):
            return VerifyVLResponse(status="success", lessonId=userData.lessonId, msg="Leccion disponible")
        
        return VerifyVLResponse(status="error", lessonId=userData.lessonId, msg="El usuario ya completo esta leccion")

    except Exception as e:
        logger.error(e)

        raise e


async def get_redis_data(redis_client: asyncredis.Redis, lesson_ids: List[str]) -> List[RedisLesson]:

    """
    Método para obtener las lecciones válidas para el usuario.

    Retorna
    -------
    Retorna lista con objetos RedisLesson las lecciones válidas para el usuario

    """
    if not lesson_ids:
        return []

    pipeline = await redis_client.pipeline()
    
    for key in lesson_ids:
        await pipeline.hgetall(key)
    
    results = await pipeline.execute()

    items = []
    for key, result in zip(lesson_ids, results):

        newValue = RedisLesson(**result)

        newValue.id = key

        items.append(newValue)

    return items
