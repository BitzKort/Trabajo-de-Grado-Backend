import asyncpg
from jose import JWTError, jwt, ExpiredSignatureError
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import  OAuth2PasswordRequestForm
from src.repository.db import get_postgres
from src.schemas.authSchemas import Login, AuthResponse, Register, ForgotPasswordRequest, UseridEmailResponse, Id
from typing import List, Annotated
from loguru import logger
from src.services.authServices import authLogin, create_token, get_current_user, createUserService, forgotPassword, send_password_email, create_password_token, resetPassword


authRouter = APIRouter()


@authRouter.post("/login", response_model=AuthResponse)
async def login(userId: AuthResponse = Depends(authLogin))->AuthResponse:

    if not userId:

        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    
    else:
        access_token = await create_token(userId, type="access")

        return AuthResponse(access_token=access_token, token_type="bearer")




@authRouter.post("/register", response_model=AuthResponse)
async def register(userId: AuthResponse = Depends(createUserService)) -> AuthResponse:

    if not userId:

        logger.error("something went wrong at creating user")

        raise HTTPException (status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="error durante el registro")
    
    else:
        
        access_token = create_token(userId, type="access")

        return AuthResponse(access_token=access_token, token_type="bearer")




@authRouter.post("/logout")
async def logout_user(response :Response):

    response.delete_cookie(
        key="refresh_token",
        path="/",
        domain="http://localhost:5173" #esto es para desarrollo local
    )
    
    return HTTPException(status_code=status.HTTP_200_OK, detail="Correct logout")




@authRouter.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(data = Depends(forgotPassword)):
    user, dbConnect = data
    # 1. Verifica que exista el usuario
    if not user:
        # Por seguridad, no reveles si no existe
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No hay una cuenta con este correo electronico.")

    token = await create_password_token(user.id, dbConnect)

    # 3. Llama al servicio de email
    await send_password_email(user.email, token)

    raise HTTPException(status_code=status.HTTP_200_OK, detail="Verifica tu correo electronico para seguir.")




@authRouter.put("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(data: Id = Depends(resetPassword)):

    if not data:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="something happend during the password reset")
    
    else:

        return {"msg":"password reset succesfully"}