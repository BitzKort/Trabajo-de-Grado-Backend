from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserRead(BaseModel):
    id: int
    username: str
    name: Optional[str]
    email: EmailStr

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    
    name: Optional[str]
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):

    email: EmailStr
    password: str