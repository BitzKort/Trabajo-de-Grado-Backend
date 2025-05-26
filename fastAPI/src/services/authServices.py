import bcrypt
import os
import asyncpg
from fastapi import HTTPException, Depends, status
from loguru import logger
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt, ExpiredSignatureError
from fastapi_mail import FastMail, MessageSchema
from tsidpy import TSID
from src.repository.authRepository import emailCheckerRepository, get_userid_by_email, set_password_recovery, verify_token_recovery, delete_token_recovery
from src.repository.userRepository import createUserRepository, update_user_password, createUserStreak, verify_user
from src.repository.db import get_postgres
from src.schemas.authSchemas import Register, EmailCheckerResponse, UseridEmailResponse, ForgotPasswordRequest, resetPasswordResponse
from src.conf.emailConf import conf


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def crypt(password: str) -> str:

    """
        Método para  encriptar la contraseña del usuario.
    
        Retorna
        -------
        La contraseña del usuario encriptada
    """


    salt = bcrypt.gensalt()  
    hashed_password = bcrypt.hashpw(password.encode(), salt)  
    return hashed_password.decode()
    

async def verify_password(password, password_hashed):

    
    """
        Método para verificar la contraseña que ingresa el usuario con la encriptada en la
        base de datos.
    
        Retorna
        -------
        boolean: True si son iguales, False si no son iguales.
    """

    response = bcrypt.checkpw(password, password_hashed)

    return response


async def create_token(user_data: str, type:str) -> str:

    """
        Método para crear el tooken de acceso.
    
        Retorna
        -------
        Token de acceso string.
    """

    ACCESS_TIME = int(os.getenv("ACCESS_TOKEN_TIME_MINUTES"))
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    if type == "access":

        token_expires = timedelta(minutes=ACCESS_TIME)

    to_encode = {"sub": user_data}
    if token_expires:
        expire = datetime.now(timezone.utc) + token_expires

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(claims= to_encode, key= SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



async def create_password_token(userId: str, dbConnect) -> str:

    """
        Método para crear el token de recuperación de la contraseña.
        Se crea un uuid que es el token que se guarda en la base de datos,
        por último se crea un token JWT.
    
        Retorna
        -------
        Token JWT string.

        Excepciones
        -------
        - Excepciones dentro de los metodos del repositorio.
    """


    try:
        SECRET_KEY = os.getenv("SECRET_KEY")
        ALGORITHM = os.getenv("ALGORITHM")

        RECOVERY_TIME = int(os.getenv("RECOVERY_TOKEN_MINUTES"))

        tokenId = str(TSID.create())
    
        token_expires = timedelta(minutes=RECOVERY_TIME) 

        token_saved = await set_password_recovery(userId,tokenId, dbConnect)

        to_encode = {"sub": token_saved.token}
        if token_expires:
            expire = datetime.now(timezone.utc) + token_expires

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(claims= to_encode, key= SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt
    
    except Exception as e:

        logger.error(e)

        raise e


async def get_current_user(token: str = Depends(oauth2_scheme), dbConnect: asyncpg.Pool = Depends(get_postgres)):

    """
        Método para verificar el token de acceso que da el usuario en cada petición.
        Este método verifica que tenga el formato válido (si es un jwt, si es de un usuario existente y si no ha caducado).
    
        Retorna
        -------
        El id del usuario: string

        Excepciones
        -------
        - JWTError: Si hay algun error con el formato del token.
        - ExpiredSignatureError: Si el token ha caducado.
        - invalid_user: Si el id que se encuentra en el JWT no pertenece a ningún usuario.
        - Excepciones dentro de los métodos del repositorio.
    """


    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token no valido",
        headers={"WWW-Authenticate": "Bearer"}
    )

    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token vencido",
        headers={"WWW-Authenticate": "Bearer"}
    )

    invalid_user = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Usuario no valido",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userId: str = payload.get("sub")
        if userId is None:
            raise credentials_exception
        
        if not await verify_user(userId, dbConnect):

            raise invalid_user

    except ExpiredSignatureError:
        raise expired_exception

    except JWTError:
        raise credentials_exception
    
    except Exception as e:
        
        raise e
    
    return userId



async def resetPassword(token:str, newPassword:str, dbConnect:asyncpg.Pool ) ->resetPasswordResponse:


    """
        Método para verificar el token JWT de cambio de contraseña enviado por correo electrónico al usuario.
    
        Retorna
        -------
        boolean: True: si el token es valido, false si no es valido.

        Excepciones
        -------
        
        - JWTError: Si hay algun error con el formato del token.
        - ExpiredSignatureError: Si el token ha caducado.
        - Excepciones dentro de los métodos del repositorio.
    """


    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token no valido.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token vencido.",
        headers={"WWW-Authenticate": "Bearer"}
    )
    

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        password_token: str = payload.get("sub")

        user = await verify_token_recovery(password_token, dbConnect)

        await delete_token_recovery(user.id, dbConnect)

        newCryptPassword = await crypt(newPassword)

        await update_user_password(user.id, newCryptPassword, dbConnect)
    
    except JWTError:
        raise credentials_exception

    except ExpiredSignatureError:
        raise expired_exception

    except Exception as e:

        logger.error(e)

        raise e

    
    return True


async def authLogin(userData: OAuth2PasswordRequestForm = Depends(), dbConnect = Depends(get_postgres)) -> EmailCheckerResponse:


    """
        Método para la logica del login.
    
        Retorna
        -------
        el Id del usuario.

        Excepciones
        -------
        
        - 404 Not Found: Usuario o contraseña incorrectos.
        - Excepciones dentro de los métodos del repositorio.
    """

    try: 
        userInfo = await emailCheckerRepository(userData.username, dbConnect)


        hashed_password = userInfo.password
        checker = await verify_password(userData.password.encode('utf-8'), hashed_password.encode('utf-8'))

        if not checker:

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario o contraseña incorrectos.", headers={"WWW-Authenticate": "Bearer"})

        else:

            return userInfo.id
    except Exception as e:

        logger.error(e)

        raise e
            

async def createUserService(userData: Register, dbConnect ) -> str:


    """
        Método para la logica del registro de usuario.
    
        Retorna
        -------
        el Id del nuevo usuario registrado.

        Excepciones
        -------
        - Excepciones dentro de los métodos del repositorio.
    """

    try:
        hashedPassword = await crypt(userData.password)

        userData.password = hashedPassword

        registerResponse =  await createUserRepository(userData, dbConnect)

        await createUserStreak(registerResponse.id, dbConnect)

        return registerResponse.id
    
    except Exception as e:
        logger.error(e)
        raise e



async def forgotPassword( emailData:ForgotPasswordRequest= Depends(), dbConect = Depends(get_postgres)):


    """
        Método para verifica que si exista un usuario con ese email.
    
        Retorna
        -------
        Objeto UseridEmailResponse y conexion a la base de datos.

        Excepciones
        -------
        - Excepciones dentro de los métodos del repositorio.
    """

    try:

        userData = await get_userid_by_email(emailData.email,dbConect)

        return UseridEmailResponse(id=userData.id, email=emailData.email), dbConect

    except Exception as e:
        logger.error(e)
        raise e

async def send_password_email(email: str, token: str):


    """
       Método para el envío del correo electrónico de recuperar contraseña.
    
        Retorna
        -------
        None
    """


    reset_link = f"http://localhost:5173/changePassword?token={token}"
    msg = MessageSchema(
        subject="Restablece tu contraseña",
        recipients=[email],
        body=f"""\
            <p>¡Hola!</p>
            <p>Haz clic en el enlace para restablecer tu contraseña:</p>
            <p><a href="{reset_link}">{reset_link}</a></p>
            <p>Si no solicitaste este correo, puedes ignorarlo.</p>
        """,
        subtype="html",
    )
    fm = FastMail(conf)
    await fm.send_message(msg) 


