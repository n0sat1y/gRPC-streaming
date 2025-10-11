from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import insert

from src.models import UserReplicaModel
from src.core.db import SessionLocal

class UserRepository:
    async def get(self, id: int, is_active: bool = True) -> UserReplicaModel:
        try:
            async with SessionLocal() as session:
                result = await session.execute(
                    select(UserReplicaModel)
                    .where(UserReplicaModel.id==id, UserReplicaModel.is_active==is_active)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f'Database Error {e}')
            await session.rollback()
            raise e
        
    async def get_multiple(self, ids: list, is_active: bool = True) -> list[UserReplicaModel]:
        try:
            async with SessionLocal() as session:
                result = await session.execute(
                    select(UserReplicaModel)
                    .where(UserReplicaModel.id.in_(ids), UserReplicaModel.is_active==is_active)
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(f'Database Error {e}')
            await session.rollback()
            raise e

    async def upsert(self, data: dict):
        try:
            async with SessionLocal() as session:
                stmt = insert(UserReplicaModel).values(
                    id=data['id'],
                    username=data['username'],
                    is_active=data.get('is_active', True)
                )
                update_stmt = stmt.on_conflict_do_update(
                    index_elements=['id'], 
                    set_=dict(
                        username=stmt.excluded.username,
                        is_active=stmt.excluded.is_active
                    )
                )
                await session.execute(update_stmt)
                await session.commit()
        except Exception as e:
            logger.error(f'Database Error {e}')
            await session.rollback()
            raise e
        
    async def deactivate(self, user_id: int):
        try:
            async with SessionLocal() as session:
                stmt = (
                    update(UserReplicaModel)
                    .where(UserReplicaModel.id == user_id)
                    .values(is_active=False)
                )
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            logger.error(f'Database Error {e}')
            await session.rollback()
            raise e
