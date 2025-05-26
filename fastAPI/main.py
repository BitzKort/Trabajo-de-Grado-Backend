import uvicorn
import dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.routes.userRoutes import userRouter
from src.routes.lessonsRouter import lessonsRouter
from src.routes.rankingRoutes import rankingRouter
from src.routes.nplRouter import nplRouter
from src.routes.authRouter import authRouter
from src.repository.db import init_postgres, close_postgres, init_redis, close_redis



@asynccontextmanager
async def lifespan(app: FastAPI):

    """
        Método inicial del servidor.
        Inicia las conexiones a las bases de datos y las cierra cuando se cierre el servidor.
    
        Retorna
        -------
        None
    """

    await init_postgres()
    await init_redis()
    yield
    await close_postgres()
    await close_redis()


dotenv.load_dotenv(dotenv_path="../.env.dev")



app = FastAPI(title = "Ogloc Server", 
              version="1.0.0",
              description="API del trabajo de grado: Prototipo Web como Soporte para la Enseñanza de Inglés a través de la Gamificación y Algoritmos de Procesamiento del Lenguaje Natural",
              lifespan=lifespan)

app.include_router(userRouter, tags=["Usuarios"])
app.include_router(lessonsRouter, tags=["Lecciones"])
app.include_router(rankingRouter, tags=["Rachas"])
app.include_router(nplRouter, tags=["PLN"])
app.include_router(authRouter, tags=["Autenticación"])


origins = [

    "http://localhost:8000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,  
    allow_methods=["*"],  
    allow_headers=["*"]
)


@app.get("/", tags=["Por defecto."])
def home ():


    """
        Ruta inicial del servidor.

        Retorna
        ------

        Json: mensaje: Servidor iniciado con éxito.
    """

    return {"msg":"Servidor iniciado con éxito."}


if __name__ == "__main__":

    uvicorn.run(app, host="localhost", port=8000)