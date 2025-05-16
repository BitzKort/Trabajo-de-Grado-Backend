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