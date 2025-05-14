from pydantic import BaseModel, ConfigDict
from datetime import datetime

#schemas for responses models

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
    last_activity_date: datetime

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
    
class UserInfoEntry(BaseModel):
    id:str


class userNameResponse(BaseModel):

    name:str
    username:str