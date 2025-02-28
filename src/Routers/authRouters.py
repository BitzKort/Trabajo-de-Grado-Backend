from fastapi import APIRouter, HTTPException, Response
from src.Schemas.userSchema import UserCreate
from src.Schemas.userSchema import UserLogin
from src.services.authServices import authLoguin, createUserService
authRouter = APIRouter()


@authRouter.post('/login', status_code=200)

async def login(userData: UserLogin):

    response = await authLoguin(userData)

    if not response:

        raise HTTPException (status_code=404, detail="usuario no encontrado")
    
    return {"message": "Usuario verificado"}
    


@authRouter.post('/register', status_code=200)

async def create_user(user: UserCreate):

    print("entra al controlador")

    print(user)

    response = await createUserService(user)

    if not response:

         return Response(status_code=500)
    
    return {"message": "Usuario creado exitosamente"}