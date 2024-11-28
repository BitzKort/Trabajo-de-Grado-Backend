from fastapi import FastAPI,  APIRouter  
from src.Routers.userRouters import router

app = FastAPI(title ="Ogloc")
print(type(router))
app.include_router(router)



if __name__ == "__main__":

    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)

