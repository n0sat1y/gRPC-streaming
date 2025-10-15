from functools import wraps
from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import IntegrityError

from src.models import UserModel
from src.core.db import SessionLocal

def with_session(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with SessionLocal() as session:
            try:
                result = await func(*args, session=session, **kwargs)
                return result
            except Exception as e:
                await session.rollback()
                logger.error(f"Database Error in {func.__name__}: {e}")
                raise 
    return wrapper

class UserRepository:
    @with_session
    async def get(self, id: int, session: AsyncSession, is_active: bool = True) -> UserModel:
        result = await session.execute(
            select(UserModel)
            .where(UserModel.id==id, UserModel.is_active==is_active)
        )
        return result.scalar_one_or_none()

    @with_session
    async def get_by_username(self, username: str, session: AsyncSession, is_active: bool = True) -> UserModel:
        result = await session.execute(
            select(UserModel)
            .where(UserModel.username == username, UserModel.is_active==is_active)
        )
        return result.scalar_one_or_none()
        
    @with_session
    async def get_multiple(self, ids: list, session: AsyncSession, is_active: bool = True) -> list[UserModel]:
        result = await session.execute(
            select(UserModel)
            .where(UserModel.id.in_(ids), UserModel.is_active==is_active)
        )
        return result.scalars().all()
        
    @with_session
    async def create(self, user_data: dict, session: AsyncSession) -> UserModel:
        try:
            user = UserModel(**user_data)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        except IntegrityError as e:
            logger.error(f'Integrity Error {e}')
            raise e

    @with_session
    async def delete(self, user_id: int, session: AsyncSession) -> None:
        stmt = (
            update(UserModel).
            where(UserModel.id == user_id)
            .values(is_active=False)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount

