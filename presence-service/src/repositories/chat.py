from loguru import logger
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from src.models import ChatMemberReplica
from src.decorators import with_session


class ChatRepository:
    @with_session
    async def insert(self, chat_id: int, members: list[int], session: AsyncSession) -> None:
        delete_stmt = delete(ChatMemberReplica).where(ChatMemberReplica.chat_id == chat_id)
        await session.execute(delete_stmt)

        if members:
            stmt = (
                insert(ChatMemberReplica)
                .values([{'chat_id': chat_id, 'user_id': user_id} for user_id in members])
                .on_conflict_do_nothing(index_elements=['chat_id', 'user_id'])
            )
            await session.execute(stmt)
            await session.commit()

    @with_session
    async def get_relations(self, user_id: int, session: AsyncSession) -> list[ChatMemberReplica]:
        subquery = (
            select(ChatMemberReplica.chat_id)
            .where(ChatMemberReplica.user_id == user_id)
        )

        user_ids = await session.execute(
            select(ChatMemberReplica.user_id)
            .where(
                ChatMemberReplica.chat_id.in_(subquery), 
                ChatMemberReplica.user_id != user_id
            )
        )
        return user_ids.scalars().all()
    
    @with_session
    async def delete_chat(self, chat_id: int, session: AsyncSession):
        stmt = (
            delete(ChatMemberReplica)
            .where(ChatMemberReplica.chat_id == chat_id)
        )        
        await session.execute(stmt)
        await session.commit()

    @with_session
    async def delete_user(self, user_id: int, session: AsyncSession):
        stmt = (
            delete(ChatMemberReplica)
            .where(ChatMemberReplica.user_id == user_id)
        )        
        await session.execute(stmt)
        await session.commit()
