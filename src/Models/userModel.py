from sqlalchemy import Column, Integer, String
from src.Repository.dbConnection import Base

class user(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable = False)
    name = Column(String, index=True, nullable=False)
    email = Column(String, nullable=False, unique=True)