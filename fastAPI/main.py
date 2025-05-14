from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.routes.userRoutes import userRouter
from src.routes.lessonsRouter import lessonsRouter
from src.routes.rankingRoutes import rankingRouter
from src.routes.nplRouter import nplRouter
from src.routes.authRouter import authRouter
from src.repository.db import init_postgres, close_postgres, init_redis, close_redis

import uvicorn
import dotenv

@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_postgres()
    await init_redis()
    yield
    await close_postgres()
    await close_redis()



dotenv.load_dotenv(dotenv_path="../.env.prod")

app = FastAPI(title = "Ogloc Backend 3.0", lifespan=lifespan)

app.include_router(userRouter, tags=["users"])
app.include_router(lessonsRouter, tags=["lessons"])
app.include_router(rankingRouter, tags=["ranking"])
app.include_router(nplRouter, tags=["npl"])
app.include_router(authRouter, tags=["auth"])

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