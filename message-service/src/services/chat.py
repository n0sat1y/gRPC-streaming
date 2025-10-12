from loguru import logger

from src.repositories.chat import ChatRepository
from src.models.replications import ChatReplica
from src.schemas.chat import ChatData, IdSchema


class ChatService():
    def __init__(self):
        self.repo = ChatRepository()

    async def upset(self, data: ChatData):
        logger.info(f"Создаем (или обновляем чат) чат {data.id}")
        print(data.model_dump())
        new_chat = await self.repo.upsert_data(data.model_dump())
        logger.info(f"Чат создан (или обновлен): ")

    async def delete(self, data: IdSchema):
        logger.info(f"Удаляем чат {data.id}")
        
        chat = await self.repo.delete(data.id)
        logger.info(f"Чат удален: {chat}")

