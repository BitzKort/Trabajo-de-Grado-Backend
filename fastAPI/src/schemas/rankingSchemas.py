from pydantic import BaseModel
from datetime import datetime
class RankingResponse(BaseModel):

    username: str
    exp: int
    days: int