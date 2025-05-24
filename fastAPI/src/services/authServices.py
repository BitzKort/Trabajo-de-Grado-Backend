import bcrypt
import os
import asyncpg
import redis.asyncio as asyncredis
from fastapi import HTTPException, Depends, status, Body
from loguru import logger
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt, ExpiredSignatureError
from fastapi_mail import FastMail, MessageSchema
from tsidpy import TSID
from src.repository.authRepository import emailCheckerRepository, get_userid_by_email, set_password_recovery, verify_token_recovery, delete_token_recovery 
from src.repository.userRepository import createUserRepository, update_user_password, createUserStreak
from src.repository.db import get_postgres, get_redis
from src.schemas.authSchemas import Register, EmailCheckerResponse, UseridEmailResponse, ForgotPasswordRequest, resetPasswordResponse
from src.conf.emailConf import conf


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def crypt(password: str) -> str:

    salt = bcrypt.gensalt()  
    hashed_password = bcrypt.hashpw(password.encode(), salt)  
    return hashed_password.decode()
    

async def verify_password(password, password_hashed):

    response = bcrypt.checkpw(password, password_hashed)

    return response


async def create_token(user_data: str, type:str) -> str:

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


async def get_current_user(redisConnect: asyncredis.Redis = Depends(get_redis), token: str = Depends(oauth2_scheme)):

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

    deleted_user = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Cuenta borrada.",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userId: str = payload.get("sub")
        if userId is None:
            raise credentials_exception
        
        if not await verify_deleted_user(userId, redisConnect):

            raise deleted_user

    except ExpiredSignatureError:
        raise expired_exception

    except JWTError:
        raise credentials_exception
    
    except Exception as e:
        
        raise e
    
    return userId



async def resetPassword(token:str, newPassword:str, dbConnect:asyncpg.Pool ) ->resetPasswordResponse:

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

    #check if the email exist in order to get the password

    try: 
        userInfo = await emailCheckerRepository(userData.username, dbConnect)


        hashed_password = userInfo.password
        checker = await verify_password(userData.password.encode('utf-8'), hashed_password.encode('utf-8'))

        if not checker:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos.", headers={"WWW-Authenticate": "Bearer"})

        else:

            return userInfo.id
    except Exception as e:

        logger.error(e)

        raise e
            

async def createUserService(userData: Register, dbConnect ) -> str:

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

    try:

        logger.warning(emailData)
        userData = await get_userid_by_email(emailData.email,dbConect)

        return UseridEmailResponse(id=userData.id, email=emailData.email), dbConect

    except Exception as e:
        logger.error(e)
        raise e

async def send_password_email(email: str, token: str):
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


async def verify_deleted_user(userId: str, redisConnect) -> bool:
    """
    - Usa el key "deleted:users" como un SET de IDs.
    - Si el key no existe, retorna True indicando de que la cuenta sigue activa.
    - Si el key existe:
        • Si el userId ya está en el set, retorna False indicando que la cuenta esta eliminada.
        • Si no está, lo añade y retorna True indicando que la cuenta esta activa.
    """
    key = "deleted:users"

    exists = await redisConnect.exists(key)
    
    if not exists:
        return True

    is_deleted = await redisConnect.sismember(key, userId)

    if is_deleted:
        return False

    return True