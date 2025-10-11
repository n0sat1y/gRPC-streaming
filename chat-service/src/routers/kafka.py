from faststream.kafka import KafkaBroker
from loguru import logger
from src.core.config import settings

from src.services.user import UserService
from src.schemas.user import UserEvent

broker = KafkaBroker(f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}")
service = UserService()

@broker.subscriber('user.event')
async def delete_user_chats(data: UserEvent):
    event = data.event_type
    data = data.data
    logger.info(f"Получено уведомление о собынии в сервисе пользователей {event}")
    if event == "UserCreated":
        await service.create_or_update(data)
    elif event == 'UserDeactivated':
        await service.deactivate(data.id)
    
    
