from src.Repository.dbConnection import get_db
from sqlalchemy.orm import Session
from src.Models.userModel import user
from fastapi import Depends, HTTPException
from src.Schemas.userSchema import UserCreate

from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
#for user login

@asynccontextmanager
async def get_db_session():
    async for session in get_db():
        yield session

async def emailCheck(email: str):
    async with get_db_session() as db:  # Obtiene la sesión igual que createUserRepository
        userData = await db.execute(select(user).where(user.email == email))
        userData = userData.scalars().first()

        if not userData:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return userData.password
    



async def createUserRepository(userData: UserCreate):
    async with get_db_session() as db:  # Obtiene la sesión aquí
        db_user = user(**userData.model_dump())
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user