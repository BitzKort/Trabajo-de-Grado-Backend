from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserRead(BaseModel):
    id: int
    username: str
    name: Optional[str]
    email: EmailStr

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    name: Optional[str]
    email: EmailStr