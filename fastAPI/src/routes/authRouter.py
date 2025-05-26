from fastapi import APIRouter, Depends, HTTPException, status, Response
from src.schemas.authSchemas import AuthResponse, Id, Register, resetPasswordEntry
from loguru import logger
from src.services.authServices import authLogin, create_token, createUserService, forgotPassword, send_password_email, create_password_token, resetPassword, get_current_user
from src.repository.db import get_postgres

authRouter = APIRouter()


@authRouter.post("/login")
async def login(userId: AuthResponse = Depends(authLogin))->AuthResponse:


    """
        Ruta para realizar login dentro del prototipo

        Retorna
        -------
        Objeto AuthResponse que contiene el token de acceso y tipo del token 

        Excepciones
        -------
        - Excepciones dentro de los metodos de servicio.
    """


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

    """
        Ruta para realizar un registro de usuario dentro del prototipo

        Retorna
        -------
        Objeto AuthResponse que contiene el token de acceso y tipo del token 

        Excepciones
        -------
        - 406 Not Acceptable: Excepciones dentro de los metodos de servicio.
    """


    try:
        
        userId = await createUserService(userData,dbConnect )

        access_token = await create_token(userId, type="access")

        return AuthResponse(access_token=access_token, token_type="bearer")
    
    except Exception as e:

        logger.error(e)

        return HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=e)



@authRouter.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(data = Depends(forgotPassword)):


    """
        Ruta para Enviar un correo con el link para recuperar la contraseña.

        Retorna
        -------
        200 ok: Revisa tu correo para seguir. 

        Excepciones
        -------
        - Excepciones dentro de los metodos de servicio.
    """


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


    """
        Ruta para realizar el cambio de contraseña del usuario.
        
        Retorna
        -------
        200 ok: Cambio de contraseña exitoso.

        Excepciones
        -------
        - Excepciones dentro de los metodos de servicio.
    """


    try:
        data = await resetPassword(token=userData.token, newPassword=userData.newPassword, dbConnect=dbConnect)
        
        if not data:

            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error en el cambio de la contraseña.")
        
        else:

            return {"msg":"Cambio de contraseña exitoso."}
    
    except Exception as e:

        logger.error(e)

        raise e


@authRouter.get("/verifyToken", status_code=status.HTTP_200_OK)
async def verify_user_endpoint(validToken: str = Depends(get_current_user)):
    
    
    """
        Ruta para verificar el token del usuario.
        
        NOTA
        ------
        Si bien todas las rutas están protegidas, es necesaria una ruta de verificación con el propósito de que la 
        página de login y register solo se puedan acceder cuando el token no sea válido.

        Retorna
        -------
        200 ok: ok

        Excepciones
        -------
        - Excepciones dentro de los metodos de servicio.
    """
    try:
      
      if validToken:
          
          raise HTTPException(status_code=status.HTTP_200_OK, detail="ok")
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error interno al verificar el usuario"
        )