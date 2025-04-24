from pydantic import BaseModel


#schemas for router responses

class QuestionCardResponse(BaseModel):

    text:str
    question:str
    answer:str


class SentenceCompareResponse(BaseModel):

    sentenceNlp: str
    sentenceUser:str
    score: str

#schemas for inner validations



#schemas for body structure