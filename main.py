from fastapi import FastAPI,  APIRouter  
from src.Routers.userRouters import read_users

app = FastAPI()

app.include_router(read_users)

@app.get("/")

def read():

    
    return {"message": "this is the home page"}


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)

