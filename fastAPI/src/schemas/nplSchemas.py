from pydantic import BaseModel
from typing import List

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
    newExp:int
    score:float
    type:str


class SentencesCompareEnrty(BaseModel):
    
    lesson_id:str
    newExp:int
    sentenceNlp: str
    sentenceUser:str
    type:str

class CompareRouterResponse(BaseModel):

    userId:str
    score:float
    msg:str