import bycript
from src.Repository.auth import emailCkeck, getPassword
from src.Repository.auth import registerUser



def crypt(password):

    pass

def checkCrypt(password, passwordb):

    if bycript.checkpw(password.encode(), passwordb):

        return True
    else:
        return False

def authLoguin(userData):
    
    userPass = userData.password


    #check if the email exist in order to get the password
    if emailCkeck(userData.email):

        passdb = getPassword(userData.email)

        if crypt(userPass, passdb):

            return True
        
        else:

            return False
    else:
        return False

def createUser(userData):

    #just register the user data to the database

    passwordHashed = crypt(userData.password)

    response = registerUser(userData)

    return response

