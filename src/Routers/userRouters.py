from fastapi import APIRouter

router = APIRouter()



@router.get('/users')

async def read_users():

    return [{"username": "Miguel"}, {"username":"aaaa"}]

@router.get('/')

async def home():

    return {"message": "this is the home page"}

