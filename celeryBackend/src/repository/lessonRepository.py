from sqlalchemy import text
from src.repository.dbConection import engine
from src.schemas.nplSchemas import QuestionCardResponse
from loguru import logger
import json
from psycopg2.extras import Json 

def insert_lesson(id: str, lesson: QuestionCardResponse):
    questions_list = [q.model_dump() for q in lesson.Questions]
    
    with engine.connect() as db:
        try:
            db.execute(
                text("""
                    INSERT INTO lessons 
                    (id, title, text, questions_count, questions)
                    VALUES (:id, :title, :text, :count, :questions)
                """),
                {
                    "id": id,
                    "title": lesson.title,
                    "text": lesson.text,
                    "count": len(lesson.Questions),
                    "questions": Json(questions_list)
                }
            )
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error insertando lección: {str(e)}")
            raise


def delete_lessons_data(redis_client):

    pipeline = redis_client.pipeline()
    deleted_counts = {'lessons': 0, 'users': 0}
    
    # Lecciones individuales
    for key in redis_client.scan_iter(match="lesson:*"):
        pipeline.delete(key)
        deleted_counts['lessons'] += 1
    
    # Progreso de usuarios
    for key in redis_client.scan_iter(match="user:*:completed"):
        pipeline.delete(key)
        deleted_counts['users'] += 1
    
    # Set global
    pipeline.delete("all_lessons")
    
    pipeline.execute()
    
    logger.info(f"deleted: {deleted_counts}")
