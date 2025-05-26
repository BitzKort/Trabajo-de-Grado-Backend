from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


"""
Modelos de pydantic para el uso tanto interno como externo de datos del usuario.
"""



class UserInfoResponse(BaseModel):
    id:str
    name:str
    username: str
    exp:int
    days:int
    ranking:int
    last_activity_date: datetime


class RegisterValidation(BaseModel):
    
    id:str


class User(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    name: str
    email: str
    password:str
    
class UserUpdateModel(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None