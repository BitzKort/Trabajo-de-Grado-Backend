from fastapi import APIRouter


authRouter = APIRouter()


@authRouter.get('/login')

async def login():

    pass

@authRouter.post('/register')

async def register():

    pass