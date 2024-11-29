from fastapi import FastAPI,  APIRouter  
from src.Routers.userRouters import userRouter
from src.Routers.authRouters import authRouter

from src.Models import userModel
from src.Repository.dbConnection import engine, get_db



app = FastAPI(title ="Ogloc")
app.include_router(userRouter)
app.include_router(authRouter)


userModel.Base.metadata.create_all(bind=engine)


@app.get('/')

async def home():

    return {"message": "this is the home page"}

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)

