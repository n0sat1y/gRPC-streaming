from faststream.kafka import KafkaBroker
from loguru import logger
from src.core.config import settings

from src.services import MessageService

broker = KafkaBroker(f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}")
service = MessageService()

@broker.subscriber('UserDeleted')
async def delete_user_messages(user_id: int):
    logger.info(f"Получено уведомление об удалении пользователя {user_id=}")
    await service.delete_user_messages(user_id)
    
