import dotenv
import os
from sqlalchemy import create_engine

dotenv.load_dotenv("../.env.dev")

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_size=50,
    max_overflow=50,
    pool_recycle=300
)
