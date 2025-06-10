from pydantic import BaseModel
from typing import List


"""
Modelos de pydantic para el uso tanto interno como externo de datos de lecciones.
"""



class LessonIdentry(BaseModel):
    lessonId:str

class SaveLessonEnrtry(BaseModel):

    newExp:int
    lessonId:str
    score:float

class LessonWithQuestions(BaseModel):
    lesson_id:str
    title: str
    text: str
    question_id:str
    question_text:str
    answer:str
    distractor:str

class ListLessonWQ(BaseModel):

    questions: List[LessonWithQuestions]

class IncorrectQuestionResponse(BaseModel):
    lesson_id: str
    question_id:str
    title: str
    text: str
    question_text: str
    answer: str
    distractor: str

class VerifyAVLResponse(BaseModel):

    status: str
    pending_lessons: list[str]
    total_pending: int


class VerifyVLResponse(BaseModel):

    status: str
    lessonId: str
    msg: str

class RedisLesson(BaseModel):

    id:str
    title:str
    question_count:int

class AVLResponse(BaseModel):

    status: str
    pending_lessons: list[RedisLesson]
    total_pending: int



