from pydantic import BaseModel, ConfigDict


#schemas for responses models

class LoginResponse(BaseModel):

    auth: str


class RankingResponse(BaseModel):

    username: str
    exp: int
    dias: int

class UserInfoResponse(BaseModel):
    name:str
    username: str
    exp:int
    dias:int
    ranking:int

class LessonResponse(BaseModel):

    id: str
    title: str
    text:str
    questions:int


#schemas for tables
class User(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    name: str
    email: str
    password:str

class Lessons(BaseModel):

    id: str
    title: str
    questions:int



class Racha(BaseModel):

    id:str
    dias: int
    exp: int
    
    
#schemas for body structure 
class Login(BaseModel):

    email: str
    password: str

class Register(BaseModel):

    name: str
    username: str
    email: str
    password: str

class UserInfoEntry(BaseModel):
    id:str



#Schemas for inner validations

class EmailCheckerResponse(BaseModel):

    id:str
    password: str

class userNameResponse(BaseModel):

    name:str
    username:str