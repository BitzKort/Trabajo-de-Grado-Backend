from fastapi import HTTPException
from tsidpy import TSID
from loguru import logger

async def insertLessons(userData, dbconect):

    id = str(TSID.create())

    query ="INSERT INTO lessons (id, title, text, questions) VALUES (($1)::text, $2, $3, $4, $5);"


    try: 
        async with dbconect.acquire() as conn:

            await conn.fetchrow(
                query,
                id,
                userData.name,
                userData.username,
                userData.email,
                userData.password
            )

            logger.success("Leccion guardada en neon")

    except Exception as e:

        logger.error(f"leccion no guardada en neon por {e}")


#toma esto con pinzas
async def complete_lesson(user: User = Depends(get_current_user)):
    today = date.today()
    if user.last_activity_date == today:
        # Ya se registró actividad hoy; no se actualiza la racha
        return {"message": "Lección ya registrada hoy."}
    elif user.last_activity_date == today - timedelta(days=1):
        # Día consecutivo; se incrementa la racha
        user.streak_count += 1
    else:
        # Día no consecutivo; se reinicia la racha
        user.streak_count = 1
    user.last_activity_date = today
    # Guarda los cambios en la base de datos
    db_session.commit()
    return {"streak": user.streak_count}

    