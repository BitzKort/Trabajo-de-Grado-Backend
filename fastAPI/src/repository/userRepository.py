
import asyncpg
from asyncpg import UniqueViolationError
from fastapi import HTTPException, status
from loguru import logger
from tsidpy import TSID
from src.schemas.userSchema import UserInfoResponse, RegisterValidation, UserUpdateModel
from datetime import datetime


async def getUserInfo(id, dbConect: asyncpg.Pool) -> UserInfoResponse:


    """
        Método para obtener la informacion general del usuario.

        Retorna
        -------
        Objeto UserInfoResponse

        Excepciones
        -------
        - Excepciones de conexión a la bd.

    """
    
    query = "SELECT id, name, username, exp, days, last_activity_date, CASE WHEN exp = 0 THEN 0 ELSE ranking END AS ranking FROM (SELECT u.id, u.name, u.username, s.exp, s.days, s.last_activity_date, DENSE_RANK() OVER (ORDER BY s.exp DESC) AS ranking FROM streaks s INNER JOIN users u  ON s.id = u.id WHERE u.deleted = FALSE) t WHERE id = $1;"

    try:

        async with dbConect.acquire() as conn:

            DBResponse = await conn.fetchrow(query, id)

            UserResponse = UserInfoResponse(**dict(DBResponse))

            return UserResponse
        
    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)


async def createUserRepository(userData, dbConect: asyncpg.Pool) -> RegisterValidation:

    """
        Método para crear un usuaro.

        Retorna
        -------
        Un objeto RegisterValidation que contiene el id del usaurio registrado.

        Excepciones
        -------
        - 409 CONFLICT si el username o el email ya están siendo utilizados por otro usuario.
        - Excepciones de conexión a la bd.

    """

    id = str(TSID.create())

    query ="INSERT INTO users (id, username, name, email, password) VALUES (($1)::text, $2, $3, $4, $5);"


    try: 
        async with dbConect.acquire() as conn:

            await conn.execute(
                query,
                id,
                userData.username,
                userData.name,
                userData.email,
                userData.password
            )

            return RegisterValidation(id=id)
        

    except UniqueViolationError as e:

            if e.constraint_name == "user_email_key" or e.constraint_name == "users_email_key" :
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El correo ya está registrado."
            )

            elif e.constraint_name == "users_username_key" or e.constraint_name == "user_username_key":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El Username ya está registrado."
            )
            
    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)



async def createUserStreak(userId: str, dbConnect):
    
    """
        Método para crear la racha del usuario.

        Retorna
        -------
        None

        Excepciones
        -------
        - Excepciones de conexión a la bd.

    """


    new_last_date = datetime.today()
    query = """
    INSERT INTO streaks (id, days, exp, last_activity_date)
    VALUES ($1, 0, 0, $2);
    """

    try:
        async with dbConnect.acquire() as conn:
            await conn.execute(query, userId, new_last_date)
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creando la racha del usuario."
        )

async def update_user_password(userId, newPassword, dbConect: asyncpg.Pool):

    """
        Método para actualizar la contraseña del usuario.

        Retorna
        -------
        None

        Excepciones
        -------
        - Excepciones de conexión a la bd.

    """

    query ="UPDATE users SET password = $2 WHERE id = $1;"

    try:

        async with dbConect.acquire() as conn:

            await conn.fetchrow(query, userId, newPassword)

    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    

async def userUpdate(user_data: UserUpdateModel, userId: str, dbConnect: asyncpg.Pool):

    """
        Método para actualizar el name o el username del usuario.

        Retorna
        -------
        None

        Excepciones
        -------
        - 404 Bad Request si ingresan valores vacios.
        - 409 CONFLICT 
        - Excepciones de conexión a la bd.

    """

    fields = []
    values = []

    if user_data.name is not None:
        fields.append("name = ${}".format(len(values) + 2))
        values.append(user_data.name)
    if user_data.username is not None:
        fields.append("username = ${}".format(len(values) + 2))
        values.append(user_data.username)

    if not fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No hay campos para actualizar.")

    query = f"UPDATE users SET {', '.join(fields)} WHERE id = $1 RETURNING id"

    try:
        async with dbConnect.acquire() as conn:
            row = await conn.fetchrow(query, userId, *values)

            if row is None:

                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

    except UniqueViolationError as e:

            if e.constraint_name == "users_username_key" or e.constraint_name == "user_username_key":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El Username ya está registrado."
            )
        

    except Exception as e:

        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    


async def deleteFromIncorrect(userId: str, question_id: str, dbConnect):
    

    """
        Método para eliminar una pregunta del pool de preguntas incorrectas del usuario.

        Retorna
        -------
        None

        Excepciones
        -------
        - Excepciones de conexión a la bd.

    """


    query = """
        DELETE FROM incorrect_questions
        WHERE user_id = $1 AND question_id = $2;
    """

    try:
        async with dbConnect.acquire() as conn:
            await conn.execute(query, userId, question_id)

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error eliminando pregunta incorrecta."
        )



async def insertIntoIncorrect(userId: str, question_id: str, dbConnect):


    """
        Método para ingresar una pregunta del pool de preguntas incorrectas del usuario.

        Retorna
        -------
        None

        Excepciones
        -------
        - Excepciones de conexión a la bd.

    """

 
    id = str(TSID.create())

    query = """
        INSERT INTO incorrect_questions (id, user_id, question_id)
        VALUES ($1, $2, $3);
    """

    try:
        async with dbConnect.acquire() as conn:
            await conn.execute(query, id, userId, question_id)

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error insertando pregunta incorrecta."
        )

async def verify_user(id:str, dbConnect: asyncpg.Pool) -> bool:
   
   
    """
        Método para verificar la existencia de un usuario.

        Retorna
        -------
        None

        Excepciones
        -------
        - Excepciones de conexión a la bd.

    """
    
    query = """
        SELECT EXISTS(
            SELECT 1 FROM users 
            WHERE id = $1
        )
    """

    try:
        async with dbConnect.acquire() as conn:
            exists = await conn.fetchval(query,id)
            return exists
            
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al verificar usuario existente."
        )