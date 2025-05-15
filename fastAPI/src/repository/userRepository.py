
from src.schemas.userSchema import UserInfoResponse, RegisterValidation, UserUpdateModel
from fastapi import HTTPException, status
import asyncpg
from loguru import logger
from tsidpy import TSID



async def getUserInfo(id, dbConect: asyncpg.Pool) -> UserInfoResponse:
    
    query =" SELECT id, name, username, exp, dias, last_activity_date, ranking FROM ( SELECT u.id, u.name, u.username, r.exp, r.dias, r.last_activity_date, DENSE_RANK() OVER (ORDER BY r.exp DESC) AS ranking FROM racha r INNER JOIN users u ON r.id = u.id) t WHERE id = $1;"

    try:

        async with dbConect.acquire() as conn:

            DBResponse = await conn.fetchrow(query, id)

            UserResponse = UserInfoResponse(**dict(DBResponse))

            return UserResponse
        
    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)


async def update_strike(userInfo, dbConect: asyncpg.pool):

    query =" UPDATE racha SET dias = $2, exp = $3, last_activity_date = $4 WHERE id = $1; RETURNING *"

    try:

        async with dbConect.acquire() as conn:

            DBResponse = await conn.fetchrow(query, userInfo.id, userInfo.dias, userInfo.exp, userInfo.last_activity_date)

            UserResponse = UserInfoResponse(**dict(DBResponse))

            return UserResponse
        
    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)



async def createUserRepository(userData, dbConect: asyncpg.Pool) -> RegisterValidation:

    id = str(TSID.create())

    query ="INSERT INTO users (id, name, username, email, password) VALUES (($1)::text, $2, $3, $4, $5) RETURNING id AS userid;"


    try: 
        async with dbConect.acquire() as conn:

           new_user = await conn.fetchrow(
                query,
                id,
                userData.name,
                userData.username,
                userData.email,
                userData.password
            )
                      
           user = RegisterValidation(**dict(new_user))
           
           logger.success("user created")

           return user 

    except Exception as e:
        logger.error(f"Error on insert user: {e}")



async def update_user_password(userId, newPassword, dbConect: asyncpg.Pool):

    query ="UPDATE users SET password = $2 WHERE id = $1;"

    try:

        async with dbConect.acquire() as conn:

            await conn.fetchrow(query, userId, newPassword)

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    

async def userUpdate(user_data: UserUpdateModel, dbConnect: asyncpg.Pool):
    fields = []
    values = []

    if user_data.name is not None:
        fields.append("name = ${}".format(len(values) + 2))
        values.append(user_data.name)
    if user_data.username is not None:
        fields.append("username = ${}".format(len(values) + 2))
        values.append(user_data.username)

    if not fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    query = f"UPDATE users SET {', '.join(fields)} WHERE id = $1 RETURNING id"

    try:
        async with dbConnect.acquire() as conn:
            row = await conn.fetchrow(query, user_data.id, *values)

            if row is None:

                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))