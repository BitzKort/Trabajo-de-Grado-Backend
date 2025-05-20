
from pydantic import BaseModel
from datetime import datetime

class Streak(BaseModel):

    id:str
    dias: int
    exp: int
    last_activity_date: datetime