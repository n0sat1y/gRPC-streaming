from loguru import logger
from sqlalchemy import select, delete, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from src.models import ChatModel, ChatMemberModel, UserReplicaModel
from src.decorators import with_session
from src.enums.enums import ChatTypeEnum
from src.dto.chat import *
from src.core.interfaces.repositories import IChatRepository

class ChatRepository(IChatRepository):
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
            select(ChatModel)
            .join(ChatMemberModel)
            .where(ChatMemberModel.user_id==user_id)
            .options(
                selectinload(ChatModel.members).selectinload(ChatMemberModel.user)
            )
        )
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
    async def get_private(self, current_user: int, target_user: int, session: AsyncSession) -> ChatModel:
        stmt = await session.execute(
            select(ChatModel)
            .join(ChatMemberModel)
            .where(
                ChatModel.chat_type == ChatTypeEnum.PRIVATE,
                ChatMemberModel.user_id.in_([current_user, target_user])
            )
            .group_by(ChatModel.id)
            .having(func.count(ChatMemberModel.user_id) == 2)
        )
        return stmt.scalar_one_or_none()
    
    @with_session
    async def create_group(self, data: CreateGroupDTO, session: AsyncSession) -> ChatModel:
        try:
            chat = ChatModel(
                name=data.name,
                avatar=data.avatar,
                chat_type=ChatTypeEnum.GROUP,
                members=[ChatMemberModel(user_id=user.id) for user in data.members]
            )
            session.add(chat)
            await session.commit()
            await session.refresh(chat, attribute_names=['members'])
            return chat
        except IntegrityError as e:
            await session.rollback()
            raise e
        
    @with_session
    async def create_private(self, current_user: int, target_user: int, session: AsyncSession) -> ChatModel:
        try:
            chat = ChatModel(
                chat_type=ChatTypeEnum.PRIVATE,
                members=[
                    ChatMemberModel(user_id=current_user),
                    ChatMemberModel(user_id=target_user)
                ]
            )
            session.add(chat)
            await session.commit()
            await session.refresh(chat)
            return chat
        except IntegrityError as e:
            await session.rollback()
            raise e
        
    @with_session
    async def update(self, chat: ChatModel, data: UpdateGroupDTO, session: AsyncSession) -> ChatModel:
        chat.avatar = data.avatar
        chat.name = data.name
        session.add(chat)
        await session.commit()
        await session.refresh(chat)
        return chat
    
    @with_session
    async def update_last_read_message(
        self, 
        chat_member: ChatMemberModel, 
        last_read_message_id: str, 
        session: AsyncSession
    ) -> ChatMemberModel:
        chat_member.last_read_message_id = last_read_message_id
        session.add(chat_member)
        await session.commit()
        await session.refresh(chat_member)
        return chat_member
        
    @with_session
    async def add_members(self, chat: ChatModel, members: list, session: AsyncSession) -> ChatModel:
        try:
            chat.members += [ChatMemberModel(user_id=id) for id in members]
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
    async def delete(self, chat_id: int, session: AsyncSession) -> int:
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
    async def delete_user_chats(self, user_id: int, session: AsyncSession) -> int:
        stmt = (
            delete(ChatMemberModel).
            where(ChatMemberModel.user_id==user_id)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount
        
    @with_session
    async def delete_user_from_chat(self, user_id: int, chat_id: int, session: AsyncSession) -> int:
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
    
    


