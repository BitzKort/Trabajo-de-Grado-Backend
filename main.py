from fastapi import FastAPI
from src.Routers.userRouters import userRouter
from src.Routers.authRouters import authRouter
from src.Routers.nlpRouters import nlpRouter
from src.Models import userModel
from src.Repository.dbConnection import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager


app = FastAPI(title ="Ogloc")
app.include_router(userRouter)
app.include_router(authRouter)
app.include_router(nlpRouter)

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Se ejecuta al iniciar y al cerrar la aplicación."""
    async with engine.begin() as conn:
        await conn.run_sync(userModel.Base.metadata.create_all)  # Crea las tablas en la BD
    yield  # Continúa con la ejecución de la aplicación


@app.get('/')

async def home():

    return {"message": "this is the home page"}

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)

