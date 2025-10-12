from faststream.kafka import KafkaBroker
from loguru import logger
from src.core.config import settings

from src.services.user import UserService
from src.services.chat import ChatService
from src.schemas.user import UserEvent
from src.schemas.message import MessageEvent

broker = KafkaBroker(f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}")
user_service = UserService()
chat_service = ChatService()

@broker.subscriber(
        'user.event',
        group_id='chat_service',
        auto_offset_reset='earliest'
    )
async def user_event(data: UserEvent):
    event = data.event_type
    data = data.data
    logger.info(f"Получено уведомление о собынии в сервисе пользователей {event}")
    if event == "UserCreated":
        await user_service.create_or_update(data)
    elif event == 'UserDeactivated':
        await user_service.deactivate(data.id)

@broker.subscriber(
        'message.event',
        group_id='chat_service',
        auto_offset_reset='earliest'
    )
async def message_event(data: MessageEvent):
    event = data.event_type
    data = data.data
    logger.info(f"Получено уведомление о собынии в сервисе сообщений {event}")
    if event == "MessageCreated":
        await chat_service.update_chat_last_message(data)

    
    
