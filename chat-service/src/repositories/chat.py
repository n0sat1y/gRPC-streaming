from loguru import logger
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from src.models import ChatModel, ChatMemberModel
from src.decorators import with_session

class ChatRepository:
    @with_session
    async def get(self, id: int, session: AsyncSession) -> ChatModel:
        stmt = await session.execute(
            select(ChatModel).
            where(ChatModel.id==id).
            options(selectinload(ChatModel.members)))
        result = stmt.scalar_one_or_none()
        return result
        
    @with_session
    async def get_by_user_id(self, user_id: int, session: AsyncSession) -> ChatModel:
        stmt = await session.execute(
            select(ChatModel).
            join(ChatMemberModel).
            where(ChatMemberModel.user_id==user_id))
        result = stmt.scalars().all()
        return result
    
    @with_session
    async def get_chat_member(self, chat_id: int, user_id: int, session: AsyncSession):
        stmt = await session.execute(
            select(ChatMemberModel).
            where(
                ChatMemberModel.user_id==user_id, 
                ChatMemberModel.chat_id==chat_id
            )
        )
        
        return stmt.scalar_one_or_none()
    @with_session
    async def create(self, chat_data: dict, members: dict, session: AsyncSession) -> ChatModel:
        try:
            chat = ChatModel(
                **chat_data,
                members=[ChatMemberModel(user_id=user['id']) for user in members]
            )
            session.add(chat)
            await session.commit()
            await session.refresh(chat, attribute_names=['members'])
            return chat
        except IntegrityError as e:
            await session.rollback()
            raise e
        
    @with_session
    async def update(self, chat: ChatModel, data: dict, session: AsyncSession) -> ChatModel:
        for key, value in data.items():
            setattr(chat, key, value)
        session.add(chat)
        await session.commit()
        await session.refresh(chat)
        return chat
        
    @with_session
    async def add_members(self, chat: ChatModel, members: list[dict], session: AsyncSession) -> ChatModel:
        try:
            chat.members += [ChatMemberModel(user_id=member_data['id']) for member_data in members]
            session.add(chat)
            await session.commit()
            await session.refresh(chat, attribute_names=['members'])
            return chat
        except IntegrityError as e:
            logger.error(f"Members already added")
            raise e
        
    @with_session
    async def update_chat_last_message(
        self, 
        chat: ChatModel, 
        last_message: str, 
        last_message_at: datetime,
        session: AsyncSession
    ) -> None:
        chat.last_message = last_message
        chat.last_message_at = last_message_at
        session.add(chat)
        await session.commit() 
        
    @with_session
    async def delete(self, chat_id: int, session: AsyncSession) -> None:
        stmt = (
            delete(ChatModel).
            where(
                ChatModel.id==chat_id
            )
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount
        
    @with_session
    async def delete_user_chats(self, user_id: int, session: AsyncSession) -> None:
        stmt = (
            delete(ChatMemberModel).
            where(ChatMemberModel.user_id==user_id)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount
        
    @with_session
    async def delete_user_from_chat(self, user_id: int, chat_id: int, session: AsyncSession) -> None:
        stmt = (
            delete(ChatMemberModel).
            where(
                ChatMemberModel.user_id==user_id, 
                ChatMemberModel.chat_id==chat_id
            )
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount
    
    


