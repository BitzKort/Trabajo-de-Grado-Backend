from pydantic import BaseModel
from typing import List
from datetime import datetime
#schemas for router responses

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


