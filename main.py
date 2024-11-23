from fastapi import FastAPI,  APIRouter  
from src.Routers.userRouters import router

app = FastAPI()
print(type(router))
app.include_router(router)


@app.get("/")

def read():

    
    return {"message": "this is the home page"}


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)

