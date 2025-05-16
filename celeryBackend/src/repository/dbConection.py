# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import dotenv
import os

dotenv.load_dotenv("../.env.dev")

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_size=15,
    max_overflow=15,
    pool_recycle=300
)

# Para uso con ORM (opcional)
SessionLocal = sessionmaker(bind=engine)