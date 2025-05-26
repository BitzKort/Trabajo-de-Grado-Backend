from loguru import logger
from tsidpy import TSID
from typing import List
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from src.repository.dbConection import engine
from src.schemas.nplSchemas import LessonData, Question

def insert_lesson(lessonData: LessonData, questions_id: list) -> str:
    """
    Inserta una nueva lección y retorna su ID generado.
    El campo questions_id se inicializa con los IDs generados.

    Retorna
    -------
    El id de la leccion.
    """
    lesson_id = str(TSID.create())

    logger.warning(lessonData)
    logger.warning(type(lessonData))
    
    try:
        stmt = text("""
            INSERT INTO lessons (id, title, text, questions_count, questions_id)
            VALUES (:id, :title, :text, :questions_count, :questions_id)
        """)

        with engine.connect() as conn:
            conn.execute(stmt, {
                "id": lesson_id,
                "title": lessonData.title,
                "text": lessonData.text,
                "questions_count": len(lessonData.Questions),
                "questions_id": JSONB().bind_processor(engine.dialect)(questions_id) 
            })
            conn.commit()

    except Exception as e:
        logger.error(e)
        raise e

    return lesson_id

def insert_questions(questions: List[Question]) -> List[str]:

    """
    Inserta preguntas y actualiza la lección con los IDs generados.
    
    Retorna 
    -------
    Lista de IDs de preguntas creadas.
    """


    question_ids: List[str] = []

    query = text("""
        INSERT INTO questions (id, question_text, answer, distractor)
        VALUES (:id, :question_text, :answer, :distractor)
    """)

    try: 
        with engine.connect() as conn:
            for question in questions:
                q_id = str(TSID.create())
                question_ids.append(q_id)

                conn.execute(query, {
                    "id": q_id,
                    "question_text": question.question,
                    "answer": question.answer,
                    "distractor": question.distractor
                })

            conn.commit()

        return question_ids
    
    except Exception as e:

        logger.error(e)

        raise e


def delete_lessons_data(redis_client):

    """
        Elimina los sets y hash de redis de lecciones y el progreso de los usuarios.
        Se hace con el fin de que al llegar las nuevas lecciones no se tengan errores
        y para que los usuarios puedan ver todas las lecciones.

        Retorna 
        -------
        None.
    """

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
