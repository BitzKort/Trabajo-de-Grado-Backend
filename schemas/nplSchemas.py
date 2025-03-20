from pydantic import BaseModel


#schemas for router responses

class QuestionCardResponse(BaseModel):

    text:str
    question:str




#schemas for inner validations



#schemas for body structure