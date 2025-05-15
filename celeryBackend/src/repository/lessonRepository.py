
from src.schemas.nplSchemas import QuestionCardResponse

def insert_lesson(id: str, lesson: QuestionCardResponse, conn) -> None:
    """
    Inserta un registro en la tabla lessons a partir del modelo Pydantic.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO lessons (id, title, text, questions, questions_count)
             VALUES (%s, %s, %s, %s)
            """,
            (id, lesson.title, lesson.text, lesson.Questions, len(lesson.Questions))
        )
    # Hacemos commit por cada inserción para evitar perder datos si falla más tarde
    conn.commit()