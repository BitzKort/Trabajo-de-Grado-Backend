import bcrypt
from src.Repository.auth import createUserRepository

from src.Repository.auth import emailCheck
from fastapi import HTTPException


def crypt(password: str) -> str:

    salt = bcrypt.gensalt()  
    hashed_password = bcrypt.hashpw(password.encode(), salt)  
    return hashed_password.decode()
    

def checkCrypt(password, passwordb):

    response = bcrypt.checkpw(password, passwordb)

    print(response)

    return response

async def authLoguin(userData):

    #check if the email exist in order to get the password
    password = await emailCheck(userData.email)
    
    return checkCrypt(userData.password.encode('utf-8'), password.encode('utf-8'))

async def createUserService(userData):

    print("entra a services")

    hashedPassword = crypt(userData.password)

    userData.password = hashedPassword

    return await createUserRepository(userData)



        
            
