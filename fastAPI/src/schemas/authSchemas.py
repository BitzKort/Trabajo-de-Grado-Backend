
from pydantic import BaseModel, EmailStr
from typing import Optional


#schemas for routers

class Login(BaseModel):

    email: EmailStr
    password: str

class Register(BaseModel):  

    name: str
    username: str
    email: EmailStr
    password: str


#Schemas for client responses
class AuthResponse(BaseModel):

    access_token: str
    token_type: str

#Schemas for inner validations
class EmailCheckerResponse(BaseModel):

    id:str
    password: str

class ForgotPasswordRequest(BaseModel):

    email: EmailStr


class UseridEmailResponse(BaseModel):

    id: str
    email:EmailStr

class resetPasswordResponse(BaseModel):

    msg:str

class Id(BaseModel):
    id:str

class Token(BaseModel):
    token:str



