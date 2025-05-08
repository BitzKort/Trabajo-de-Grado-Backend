from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.routes.userRoutes import userRouter
from src.routes.lessonsRouter import lessonsRouter
from src.routes.rankingRoutes import rankingRouter
from src.routes.nplRouter import nplRouter
from src.repository.db import init_postgres, close_postgres
from src.services.nplServices import init_models
import uvicorn
import dotenv
import os

dotenv.load_dotenv(dotenv_path="../.env.prod")

stsb_path = os.getenv("STSB_PATH")

@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_postgres()
    await init_models(stsb_path)
    yield
    await close_postgres()


app = FastAPI(title = "Ogloc Backend 3.0", lifespan=lifespan)

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