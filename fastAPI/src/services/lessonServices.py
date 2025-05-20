import redis
from fastapi import Depends, HTTPException, status
from loguru import logger
from src.services.userServices import get_current_user
from src.repository.db import get_redis
from src.schemas.lessonSchemas import VerifyAVLResponse, VerifyVLResponse, AllLessonIdentry, LessonIdentry

async def verify_all_valid_lessons(redisConnect: redis, lessonData: AllLessonIdentry = Depends(), token: str = Depends(get_current_user)) -> VerifyAVLResponse:
   
    try:
    
        all_lessons = "all_lessons"
        
        if not redisConnect.exist(all_lessons):

            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="nuevas lecciones se estan generandos")
        
        user_key = f"user:{lessonData.UserId}:completed"
        if not redisConnect.exists(user_key):
        
            return VerifyAVLResponse(status="success", pending_lessons=list(all_lessons), total_pending=len(all_lessons))
        
       
        user_completed = redisConnect.smembers(user_key)
        pending_lessons = list(set(all_lessons) - set(user_completed))
        
        return VerifyAVLResponse(status="success", pending_lessons=pending_lessons, total_pending=len(pending_lessons))
    
    except Exception as e:

        logger.error(e)
        raise e

async def verify_valid_lesson(redisConnect: redis, userData: LessonIdentry = Depends(), token: str = Depends(get_current_user)) -> VerifyVLResponse:

    try:

        if not redisConnect.exist("all_lessons"):

            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="nuevas lecciones se estan generandos")
        
        if not redisConnect.sismember("all_lessons", userData.lessonId):
            return VerifyVLResponse(status="error", lessonId=userData.lessonId, msg="La leccion no existe")
        
        user_key = f"user:{userData.UserId}:completed"
        if not redisConnect.exists(user_key):
            return VerifyVLResponse(status="success", lessonId=userData.lessonId, msg="Leccion disponible")
        
        if not redisConnect.sismember(user_key, userData.lessonId):
            return VerifyVLResponse(status="success", lessonId=userData.lessonId, msg="Leccion disponible")
        
        return VerifyVLResponse(status="error", lessonId=userData.lessonId, msg="El usuario ya completo esta leccion")

    except Exception as e:
        logger.error(e)

        raise e