from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os


load_dotenv(dotenv_path=".env.development")


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")


if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

print(SQLALCHEMY_DATABASE_URL) 


engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, connect_args={"ssl": "require"})


AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session