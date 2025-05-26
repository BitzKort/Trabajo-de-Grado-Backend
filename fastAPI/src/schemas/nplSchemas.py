from pydantic import BaseModel
from typing import List
from datetime import datetime



"""
Modelos de pydantic para el uso tanto interno como externo de datos de preguntas de lecciones y respuestas del modelo de npl
"""


class Question(BaseModel):

    question:str

class QuestionCardResponse(BaseModel):

    title:str
    text:str
    Questions: List[Question]


class SentenceCompareResponse(BaseModel):

    userId:str
    lesson_id:str
    question_id:str
    newExp:int
    score:str
    type:int


class SentencesCompareEnrty(BaseModel):
    
    lesson_id:str
    question_id:str
    newExp:int
    sentenceNlp: str
    sentenceUser:str
    type:int

class CompareRouterResponse(BaseModel):

    status:str
    userId:str
    score:str
    msg:str


