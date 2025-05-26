
from pydantic import BaseModel
from datetime import datetime

"""
Modelos de pydantic para el uso tanto interno como externo de datos de las rachas.
"""



class Streak(BaseModel):

    id:str
    dias: int
    exp: int
    last_activity_date: datetime

class LastActivityDate(BaseModel):

    last_activity_date: datetime