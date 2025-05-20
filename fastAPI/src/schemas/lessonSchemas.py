from pydantic import BaseModel


class LessonIdentry(BaseModel):

    lessonId:str
    UserId:str


class SaveLessonEnrtry(BaseModel):

    userId:str
    newExp:int
    lessonId:str
    score:float



class AllLessonIdentry(BaseModel):

    UserId:str



class VerifyAVLResponse(BaseModel):

    status: str
    pending_lessons: list[str]
    total_pending: int


class VerifyVLResponse(BaseModel):

    status: str
    lessonId: str
    msg: str


