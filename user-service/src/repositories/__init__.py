from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import IntegrityError

from src.models import UserModel
from src.core.db import SessionLocal

class UserRepository:
    async def get(self, id: int, is_active: bool = True) -> UserModel:
        try:
            async with SessionLocal() as session:
                result = await session.execute(
                    select(UserModel)
                    .where(UserModel.id==id, UserModel.is_active==is_active)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f'Database Error {e}')
            raise e

    async def get_by_username(self, username: str, is_active: bool = True) -> UserModel:
        try:
            async with SessionLocal() as session:
                result = await session.execute(
                    select(UserModel)
                    .where(UserModel.username == username, UserModel.is_active==is_active)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f'Database Error {e}')
            raise e
        
    async def get_multiple(self, ids: list, is_active: bool = True) -> list[UserModel]:
        try:
            async with SessionLocal() as session:
                result = await session.execute(
                    select(UserModel)
                    .where(UserModel.id.in_(ids), UserModel.is_active==is_active)
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(f'Database Error {e}')
            raise e
        
    async def create(self, user_data: dict) -> UserModel:
        async with SessionLocal() as session:
            try:
                user = UserModel(**user_data)
                session.add(user)
                await session.commit()
                await session.refresh(user)
                return user
            except IntegrityError as e:
                raise e
            except Exception as e:
                logger.error(f'Database Error {e}')
                raise e
        
    async def delete(self, user_id: int) -> None:
        try:
            async with SessionLocal() as session:
                stmt = (
                    update(UserModel).
                    where(UserModel.id == user_id)
                    .values(UserModel.is_active == False)
                )
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount
        except Exception as e:
            logger.error(f'Database Error {e}')
            raise e
