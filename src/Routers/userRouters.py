from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.Models import userModel
from src.Schemas import userSchema
from src.Repository.dbConnection import engine, get_db
userRouter = APIRouter()



@userRouter.get('/users')

async def read_users():

    return [{"username": "Miguel"}, {"username":"aaaa"}]


@userRouter.post("/create/", response_model=userSchema.UserCreate)
def create_user(user: userSchema.UserCreate, db: Session = Depends(get_db)):
    db_user = userModel.user(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

