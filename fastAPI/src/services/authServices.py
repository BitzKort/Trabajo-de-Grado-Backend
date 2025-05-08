import bcrypt
from fastapi import HTTPException
from src.repository.authRepository import emailCheckerRepository, createUserRepository
from loguru import logger
from schemas.userSchema import LoginResponse

def crypt(password: str) -> str:

    salt = bcrypt.gensalt()  
    hashed_password = bcrypt.hashpw(password.encode(), salt)  
    return hashed_password.decode()
    

def checkCrypt(password, passwordb):

    response = bcrypt.checkpw(password, passwordb)

    return response

async def authLogin(userData, dbconect):

    #check if the email exist in order to get the password
    response = await emailCheckerRepository(userData.email, dbconect)

    password = response.password
    
    checker = checkCrypt(userData.password.encode('utf-8'), password.encode('utf-8'))


    if checker:

        return LoginResponse(auth = response.id)
    
    else:
        raise HTTPException(status_code=401, detail="no autorizado")

async def createUserService(userData,  dbconect):

    hashedPassword = crypt(userData.password)

    userData.password = hashedPassword

    return await createUserRepository(userData,  dbconect)



        
            
