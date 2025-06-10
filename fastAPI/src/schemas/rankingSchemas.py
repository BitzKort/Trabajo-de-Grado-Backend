from pydantic import BaseModel
from datetime import datetime


"""
Modelos de pydantic para el uso tanto interno como externo de datos del ranking.
"""


class RankingResponse(BaseModel):

    username: str
    exp: int
    days: int