from loguru import logger

from src.repositories.chat import ChatRepository
from src.models.replications import ChatReplica
from src.schemas.chat import ChatData, IdSchema
from src.services.user import UserService


class ChatService():
    def __init__(
        self,
        repo: ChatRepository,
        user_service: UserService
    ):
        self.repo = repo
        self.user_service = user_service

    async def get(self, chat_id: int) -> ChatReplica:
        logger.info(f"Получаем чат {chat_id}")
        chat = await self.repo.get(chat_id)
        logger.info(f"Чат полчен: {chat_id}")
        return chat

    async def upsert(self, data: ChatData):
        logger.info(f"Создаем (или обновляем чат) чат {data.id}")
        print(data.model_dump())
        new_chat = await self.repo.upsert_data(data.model_dump())
        logger.info(f"Чат создан (или обновлен): {data.id}")

    async def delete(self, data: IdSchema):
        logger.info(f"Удаляем чат {data.id}")
        chat = await self.repo.delete(data.id)
        logger.info(f"Чат удален: {chat}")

    async def get_active_members(self, chat_id: int):
        logger.info(f"Получаем активных участников чата {chat_id}")

        chat = await self.get(chat_id)

        users = await self.user_service.get_multiple(chat.members)
        active_recievers = [
            member.user_id for member in users 
            if member.is_active == True
        ]

        return active_recievers

