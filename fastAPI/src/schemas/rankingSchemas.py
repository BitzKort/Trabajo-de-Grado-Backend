from pydantic import BaseModel

class RankingResponse(BaseModel):

    username: str
    exp: int
    dias: int