from pydantic import BaseModel
from typing import List

#schemas for router responses

class Distractor(BaseModel):

    distractor:str

class Question(BaseModel):

    question:str
    answer: str
    Distractors:List[Distractor]

class QuestionCardResponse(BaseModel):
    title:str
    text:str
    Questions: List[Question]

class SentenceCompareResponse(BaseModel):

    sentenceNlp: str
    sentenceUser:str
    score: str

#schemas for inner validations



#schemas for body structure