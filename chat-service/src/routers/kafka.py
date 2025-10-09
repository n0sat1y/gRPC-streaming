from faststream.kafka import KafkaBroker
from loguru import logger
from src.core.config import settings

from src.services import ChatService

broker = KafkaBroker(f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}")
service = ChatService()

@broker.subscriber('UserDeleted')
async def delete_user_chats(user_id: int):
    logger.info(f"Получено уведомление об удалении пользователя {user_id=}")
    await service.delete_user_chats(user_id)
