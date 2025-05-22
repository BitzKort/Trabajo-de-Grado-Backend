
import asyncpg
from asyncpg import UniqueViolationError
from fastapi import HTTPException, status
from loguru import logger
from tsidpy import TSID
from src.schemas.userSchema import UserInfoResponse, RegisterValidation, UserUpdateModel
from datetime import datetime


async def getUserInfo(id, dbConect: asyncpg.Pool) -> UserInfoResponse:
    
    query =" SELECT id, name, username, exp, days, last_activity_date, ranking FROM ( SELECT u.id, u.name, u.username, s.exp, s.days, s.last_activity_date, DENSE_RANK() OVER (ORDER BY s.exp DESC) AS ranking FROM streaks s INNER JOIN users u ON s.id = u.id) t WHERE id = $1;"

    try:

        async with dbConect.acquire() as conn:

            DBResponse = await conn.fetchrow(query, id)

            UserResponse = UserInfoResponse(**dict(DBResponse))

            return UserResponse
        
    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)


async def createUserRepository(userData, dbConect: asyncpg.Pool) -> RegisterValidation:

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

            return RegisterValidation(**dict(id))
        

    except UniqueViolationError as e:
           
           raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
            
    except Exception as e:
        logger.error(f"Error ingresando el usuario: {e}")

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)



async def createUserStreak(userId: str, dbConnect):
    

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

    query ="UPDATE users SET password = $2 WHERE id = $1;"

    try:

        async with dbConect.acquire() as conn:

            await conn.fetchrow(query, userId, newPassword)

    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    

async def userUpdate(user_data: UserUpdateModel, userId: str, dbConnect: asyncpg.Pool):
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

    except Exception as e:

        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    


async def deleteFromIncorrect(userId: str, question_id: str, dbConnect):
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