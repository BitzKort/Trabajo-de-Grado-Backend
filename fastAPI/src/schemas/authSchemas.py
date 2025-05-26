
from pydantic import BaseModel, EmailStr


""" 
Modelos de pydantic para el uso tanto interno como externo de datos en el proceso de autenticación.

"""

class Login(BaseModel):

    email: EmailStr
    password: str

class Register(BaseModel):  

    name: str
    username: str
    email: EmailStr
    password: str

class AuthResponse(BaseModel):

    access_token: str
    token_type: str

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

class resetPasswordEntry(BaseModel):

    token:str
    newPassword:str

class Id(BaseModel):
    id:str

class Token(BaseModel):
    token:str



