from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from src.models import UserReplicaModel
from src.decorators import with_session

class UserRepository:
    @with_session
    async def get(self, id: int, session: AsyncSession, is_active: bool = True) -> UserReplicaModel:
        result = await session.execute(
            select(UserReplicaModel)
            .where(UserReplicaModel.id==id, UserReplicaModel.is_active==is_active)
        )
        return result.scalar_one_or_none()
        
    @with_session
    async def get_multiple(self, ids: list, session: AsyncSession, is_active: bool = True) -> list[UserReplicaModel]:
        result = await session.execute(
            select(UserReplicaModel)
            .where(UserReplicaModel.id.in_(ids), UserReplicaModel.is_active==is_active)
        )
        return result.scalars().all()

    @with_session
    async def upsert(self, data: dict, session: AsyncSession):
        stmt = insert(UserReplicaModel).values(
            id=data['id'],
            username=data['username'],
            avatar=data['avatar'],
            is_active=data.get('is_active', True)
        )
        update_stmt = stmt.on_conflict_do_update(
            index_elements=['id'], 
            set_=dict(
                username=stmt.excluded.username,
                avatar=stmt.excluded.avatar,
                is_active=stmt.excluded.is_active
            )
        )
        await session.execute(update_stmt)
        await session.commit()

    @with_session
    async def deactivate(self, user_id: int, session: AsyncSession):
        stmt = (
            update(UserReplicaModel)
            .where(UserReplicaModel.id == user_id)
            .values(is_active=False)
        )
        await session.execute(stmt)
        await session.commit()
