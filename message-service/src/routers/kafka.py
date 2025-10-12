from faststream.kafka import KafkaBroker
from loguru import logger
from src.core.config import settings

from src.services.user import UserService
from src.schemas.user import UserEvent
from src.services.chat import ChatService
from src.schemas.chat import ChatEvent

broker = KafkaBroker(f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}")
user_service = UserService()
chat_service = ChatService()

@broker.subscriber('user.event')
async def user_event(data: UserEvent):
    event = data.event_type
    data = data.data
    logger.info(f"Получено уведомление о собынии в сервисе пользователей {event}")
    if event == "UserCreated":
        await user_service.create(data)
    elif event == 'UserDeactivated':
        await user_service.deactivate(data)

@broker.subscriber('chat.events')
async def chat_event(data: ChatEvent):
    event = data.event_type
    data = data.data
    logger.info(f"Получено уведомление о собынии в сервисе чатов {event}")
    if event == "ChatCreated" or event == "ChatUpdated":
        await chat_service.upset(data)
    elif event == 'ChatDeleted':
        await chat_service.delete(data)
    
    
