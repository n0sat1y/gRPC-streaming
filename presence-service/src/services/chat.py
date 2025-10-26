from loguru import logger

from src.repositories.chat import ChatRepository
from src.models import ChatMemberReplica
from src.schemas.chat import ChatData, IdSchema


class ChatService():
    def __init__(self):
        self.repo = ChatRepository()

    async def insert(self, chat_id: int, members: list) -> None:
        logger.info(f"Вставляем пользователей в чат {chat_id}")
        print(chat_id, members)
        await self.repo.insert(chat_id, members)
        logger.info(f"Список участников чата {chat_id} обновлен")

    async def get_relations(self, user_id: int) -> list[int]:
        logger.info(f"Получаем все отношения пользователя {user_id}")
        result = await self.repo.get_relations(user_id)
        logger.info(f"Отношения пользователя {user_id} получены")
        return result
    
    async def delete_chat(self, chat_id: int) -> None:
        logger.info(f"Удаляем чат {chat_id}")
        await self.repo.delete_chat(chat_id)
        logger.info(f"Чат {chat_id} удален")

    async def delete_user(self, user_id: int) -> None:
        logger.info(f"Удаляем пользователя {user_id}")
        await self.repo.delete_user(user_id)
        logger.info(f"Пользователь {user_id} удален")


