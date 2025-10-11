from collections import defaultdict
from loguru import logger
from faststream.kafka import KafkaBroker

from src.repositories import MessageRepository
from src.models import Message


class MessageService:
    def __init__(self):
        self.repo = MessageRepository()

    async def get_all(self, chat_id: int):
        result = await self.repo.get_all(chat_id)
        logger.info(f"Получено {len(result)} сообщений из чата {chat_id=}")
        return result
    
    async def insert(self, user_id: int, chat_id: int, content: str, broker: KafkaBroker):
        message = Message(user_id=user_id, chat_id=chat_id, content=content)
        message = await self.repo.insert(message)
        logger.info(f"Добавлено сообщение {message.id=} в {chat_id=}")

        print(message.__dict__)
        await broker.publish(message.__dict__, 'MessageCreated')
        logger.info(f"Уведомление о создании сообщения {message.id} отправлено")

        return message
    
    async def delete_user_messages(self, user_id: int):
        deleted_count = await self.repo.delete_user_messages(user_id)
        logger.info(f"Удалены {deleted_count} сообщения пользователя: {user_id=}")

class ConnectionService:
    def __init__(self):
        self.active_connections = defaultdict(list)
        
    def connect(self, chat_id: int, stream):
        self.active_connections[chat_id].append(stream)
    
    def disconnect(self, chat_id: int, stream):
        self.active_connections[chat_id].remove(stream)

    async def broabcast(self, chat_id: int, message):
        for stream in self.active_connections[chat_id]:
            await stream.write(message)



