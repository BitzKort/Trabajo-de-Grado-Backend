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

    sentenceNlp: str
    sentenceUser:str
    score: str

#schemas for inner validations



#schemas for body structure