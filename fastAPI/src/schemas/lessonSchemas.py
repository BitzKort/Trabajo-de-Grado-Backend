from pydantic import BaseModel
from typing import List

class LessonIdentry(BaseModel):
    lessonId:str


class SaveLessonEnrtry(BaseModel):

    newExp:int
    lessonId:str
    score:float

#for lesson id router

class LessonWithQuestions(BaseModel):
    id:str
    title: str
    text: str
    question_id:str
    question_text:str
    answer:str
    distractor:str

class ListLessonWQ(BaseModel):

    questions: List[LessonWithQuestions]

#for failed questions router

class IncorrectQuestionResponse(BaseModel):
    id: str
    title: str
    text: str
    question_text: str
    answer: str
    distractor: str

    class Config:
        populate_by_name = True

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



