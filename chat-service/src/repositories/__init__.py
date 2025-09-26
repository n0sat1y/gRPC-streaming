from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from src.models import ChatModel, ChatMemberModel
from src.core.db import SessionLocal
from src.schemas import *

class ChatRepository:
    async def get(self, id: int) -> ChatModel:
        try:
            async with SessionLocal() as session:
                stmt = await session.execute(
                    select(ChatModel).
                    where(ChatModel.id==id).
                    options(selectinload(ChatModel.members)))
                result = stmt.scalar_one_or_none()
                return result
        except Exception as e:
            logger.error(f'Database Error {e}')
            raise e
        
    async def get_by_user_id(self, user_id: int) -> ChatModel:
        try:
            async with SessionLocal() as session:
                stmt = await session.execute(
                    select(ChatModel).
                    join(ChatMemberModel).
                    where(ChatMemberModel.user_id==user_id))
                result = stmt.scalars().all()
                return result
        except Exception as e:
            logger.error(f'Database Error {e}')
            raise e
        
    async def create(self, chat_data: dict, members: dict):
        try:
            async with SessionLocal() as session:
                chat = ChatModel(
                    **chat_data,
                    members=[ChatMemberModel(user_id=user['id']) for user in members]
                )
                session.add(chat)
                await session.commit()
                await session.refresh(chat)
                return GetChatData.model_validate(chat)
        except IntegrityError as e:
            raise e
        except Exception as e:
            logger.error(f'Database Error {e}')
            raise e
        
    async def add_members(self, chat: ChatModel, new_members: list):
        try:
            async with SessionLocal() as session:
                chat.members += [ChatMemberModel(user_id=member_data['id']) for member_data in new_members]
                session.add(chat)
                await session.commit()
                await session.refresh(chat)
                return chat
        except Exception as e:
            logger.error(f'Database Error {e}')
            raise e 
        

