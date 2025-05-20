from pydantic import BaseModel
from typing import List



class Question(BaseModel):

    question:str
    answer: str
    distractor: str

class LessonData(BaseModel):
    title:str
    text:str
    Questions: List[Question]

class RedisSave(BaseModel):

    id:str
    title:str
    question_count:int
