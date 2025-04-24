from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes.userRoutes import userRouter
from routes.lessonsRouter import lessonsRouter
from routes.rankingRoutes import rankingRouter
from routes.nplRouter import nplRouter
from repository.db import init_postgres, close_postgres
from services.nplServices import init_models
import uvicorn
import dotenv
import os

dotenv.load_dotenv(dotenv_path=".env")

gpt_path = os.getenv("GPT2_PATH")
race_path = os.getenv("RACE_PATH")
squad_path = os.getenv("SQUAD_PATH")
stsb_path = os.getenv("STSB_PATH")

@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_postgres()
    await init_models(gpt_path, race_path, squad_path, stsb_path )
    yield
    await close_postgres()


app = FastAPI(title = "Ogloc Backend 2.0", lifespan=lifespan)

app.include_router(userRouter)
app.include_router(lessonsRouter)
app.include_router(rankingRouter)
app.include_router(nplRouter)

origins = [

    "http://localhost:8000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permitir estos orígenes
    allow_credentials=True,  # Permitir credenciales (cookies, tokens, etc.)
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)




@app.get("/")

def home ():

    return {"msg":"Ogloc server started"}


if __name__ == "__main__":

    uvicorn.run(app, host="localhost", port=8000)