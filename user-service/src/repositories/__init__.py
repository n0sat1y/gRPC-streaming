from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import IntegrityError

from src.models import UserModel
from src.core.db import SessionLocal

class UserRepository:
    async def get(self, id: int) -> UserModel:
        try:
            async with SessionLocal() as session:
                result = await session.execute(select(UserModel).where(UserModel.id==id))
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f'Database Error {e}')
            raise e

    async def get_by_username(self, id: int) -> UserModel:
        try:
            async with SessionLocal() as session:
                result = await session.execute(select(UserModel))
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f'Database Error {e}')
            raise e
        
    async def create(self, user_data: dict) -> UserModel:
        try:
            async with SessionLocal() as session:
                user = UserModel(**user_data)
                session.add(user)
                await session.commit()
                await session.refresh(user)
                return user
        except IntegrityError as e:
            logger.error(f'Database Error {e}')
            raise e
