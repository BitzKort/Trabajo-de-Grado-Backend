from fastapi import APIRouter, Depends, HTTPException, status, Response
from src.schemas.authSchemas import AuthResponse, Id, Register, resetPasswordEntry
from loguru import logger
from src.services.authServices import authLogin, create_token, createUserService, forgotPassword, send_password_email, create_password_token, resetPassword
from src.repository.db import get_postgres

authRouter = APIRouter()


@authRouter.post("/login")
async def login(userId: AuthResponse = Depends(authLogin))->AuthResponse:


    try: 
        if not userId:

            raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail="usuario o contraseña incorrectos.", headers={"WWW-Authenticate": "Bearer"})
        
        else:
            access_token = await create_token(userId, type="access")

            return AuthResponse(access_token=access_token, token_type="bearer")
    
    except Exception as e:

        logger.error(e)

        raise e




@authRouter.post("/register")
async def register(userData: Register, dbConnect= Depends(get_postgres)):

    try:
        
        userId = await createUserService(userData,dbConnect )

        access_token = await create_token(userId, type="access")

        return AuthResponse(access_token=access_token, token_type="bearer")
    
    except Exception as e:

        logger.error(e)

        return HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=e)



@authRouter.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(data = Depends(forgotPassword)):


    try: 
        user, dbConnect = data
        # 1. Verifica que exista el usuario

        token = await create_password_token(user.id, dbConnect)

        # 3. Llama al servicio de email
        await send_password_email(user.email, token)

        raise HTTPException(status_code=status.HTTP_200_OK, detail="Revisa tu correo para seguir.")
    
    except Exception as e:

        raise e




@authRouter.put("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(userData: resetPasswordEntry, dbConnect = Depends(get_postgres)):


    try:
        data = await resetPassword(token=userData.token, newPassword=userData.newPassword, dbConnect=dbConnect)
        
        if not data:

            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error en el cambio de la contraseña.")
        
        else:

            return {"msg":"Cambio de contraseña exitoso."}
    
    except Exception as e:

        logger.error(e)

        raise e