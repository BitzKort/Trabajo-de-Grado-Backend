from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.Models import userModel
from src.Schemas import userSchema
from src.Repository.dbConnection import engine, get_db
userRouter = APIRouter()



@userRouter.get('/users')

async def read_users():

    return [{"username": "Miguel"}, {"username":"aaaa"}]




