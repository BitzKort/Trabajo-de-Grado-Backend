import asyncpg
from fastapi import HTTPException, status
from loguru import logger
from src.schemas.userSchema import UserInfoResponse
from src.schemas.streakSchemas import Streak, LastActivityDate

async def update_strike(userInfo, dbConect: asyncpg.pool):

    """
        Método para actualizar la racha del usuario.

        Retorna
        -------
        Un objeto Streak con los datos de la racha actualizados.

        Excepciones
        -------
        - Excepciones de conexión a la bd.

    """

    query =" UPDATE streaks SET days = $2, exp = $3, last_activity_date = $4 WHERE id = $1 RETURNING * ;"

    try:

        async with dbConect.acquire() as conn:

            DBResponse = await conn.fetchrow(query, userInfo.id, userInfo.days, userInfo.exp, userInfo.last_activity_date)

            UserResponse = Streak(**dict(DBResponse))

            return UserResponse
        
    except Exception as e:

        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)



async def get_last_activity_date(userId: str, dbConnect):

    """
        Método para obtener la fecha de la última actividad del usuario (fecha de la última pregunta realizada)

        Retorna
        -------
        Un objeto LastActivityDate con la última fecha registrada de la racha del usuario.

        Excepciones
        -------
        - 404 Not Found si la racha no fue encontrada.
        - Excepciones de conexión a la bd.

    """
    
    
    query = "SELECT last_activity_date FROM streaks WHERE id = $1;"

    try:
        async with dbConnect.acquire() as conn:
            old_last_time = await conn.fetchrow(query, userId)
            
            if old_last_time:
                return LastActivityDate(**dict(old_last_time))
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="racha no encontrada."
                )
    except HTTPException:

        raise


    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo la última actividad del usuario."
        )


async def update_days(user_id: str, dbConnect):

    """
        Método para actualizar los dias en la racha del usuario.

        Retorna
        -------
        None

        Excepciones
        -------
        - Excepciones de conexión a la bd.

    """

   
    query = """
        UPDATE streaks SET days = days + 1 WHERE id = $1;
    """

    try:
        async with dbConnect.acquire() as conn:
            await conn.execute(query, user_id)

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error actualizando los dias del usuario."
        )


async def update_exp(userId, newExp, newLastTime, dbConect: asyncpg.pool):

    """
        Método para actualizar la experiencia del usuario.

        Retorna
        -------
        None

        Excepciones
        -------
        - Excepciones de conexión a la bd.

    """

    query =" UPDATE streaks SET exp = exp + $2, last_activity_date = $3 WHERE id = $1;"

    try:

        async with dbConect.acquire() as conn:

            await conn.fetchrow(query, userId, newExp, newLastTime)
        
    except Exception as e:
                
        logger.error(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

