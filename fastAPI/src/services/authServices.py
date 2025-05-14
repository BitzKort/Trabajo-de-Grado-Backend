import bcrypt
import os
from fastapi import HTTPException, Depends, status
from loguru import logger
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt, ExpiredSignatureError

from src.repository.authRepository import emailCheckerRepository, createUserRepository
from src.repository.db import get_postgres
from src.schemas.authSchemas import AuthResponse, Register, Login, EmailCheckerResponse


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def crypt(password: str) -> str:

    salt = bcrypt.gensalt()  
    hashed_password = bcrypt.hashpw(password.encode(), salt)  
    return hashed_password.decode()
    

def verify_password(password, password_hashed):

    response = bcrypt.checkpw(password, password_hashed)

    return response


def create_token(user_data: str, type:str) -> str:

    ACCESS_TIME = int(os.getenv("ACCESS_TOKEN_TIME_MINUTES"))
    REFRESH_TIME = int(os.getenv("REFRESH_TOKEN_TIME_MINUTES"))
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    if type == "access":

        token_expires = timedelta(minutes=ACCESS_TIME)
    
    elif type == "refresh":

        token_expires = timedelta(minutes=REFRESH_TIME)

    to_encode = {"sub": user_data}
    if token_expires:
        expire = datetime.now(timezone.utc) + token_expires

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(claims= to_encode, key= SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def get_current_user(token: str = Depends(oauth2_scheme)):

    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token_invalid",
        headers={"WWW-Authenticate": "Bearer"}
    )

    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token_expired",
        headers={"WWW-Authenticate": "Bearer"}
    )

    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userId: str = payload.get("sub")
        if userId is None:
            raise credentials_exception
    
    except ExpiredSignatureError:
        raise expired_exception

    except JWTError:
        raise credentials_exception
    
    return userId


async def authLogin(userData: OAuth2PasswordRequestForm = Depends(), dbConnect = Depends(get_postgres)) -> EmailCheckerResponse:

    #check if the email exist in order to get the password
    userInfo = await emailCheckerRepository(userData.username, dbConnect)

    if not userInfo:

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    
    else:

        hashed_password = userInfo.password
        checker = verify_password(userData.password.encode('utf-8'), hashed_password.encode('utf-8'))

        if not checker:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})

        else:

            return userInfo.id
            

async def createUserService(userData: Register = Depends(), dbConnect = Depends(get_postgres)) -> str:

    hashedPassword = crypt(userData.password)

    userData.password = hashedPassword

    registerResponse =  await createUserRepository(userData, dbConnect)

    if not registerResponse:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in user creation")
    
    else:

        return registerResponse.userid


        
            
