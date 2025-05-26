from fastapi import Depends, HTTPException, status
from loguru import logger
from typing import List
from src.repository.rankingRepository import getRanking
from src.services.authServices import get_current_user
from src.repository.db import get_postgres
from src.schemas.rankingSchemas import RankingResponse


async def ranking(dbConnect = Depends(get_postgres), userId = Depends(get_current_user)) -> List[RankingResponse]:

    """
        Método para obtener el ranking de usuarios.
    
        Retorna
        -------
        Lista de objetos RankingResponse que contiene la informacion de los usuarios del ranking

        Excepciones
        -------
        - Excepciones dentro de los metodos del repositorio.
    """
    
    try:
        ranking = await getRanking(dbConnect)

        if not ranking:

            
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retornando el ranking.")
        
        return ranking
    
    except Exception as e:
        logger.error(e)
        raise e