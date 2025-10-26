from loguru import logger
from faststream.kafka import KafkaBroker
from pydantic import TypeAdapter

from src.core.config import settings
from src.schemas.chat import ChatEvent
from src.schemas.user import UserEvent
from src.services.chat import ChatService

broker = KafkaBroker(f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}")
chat_service = ChatService()

@broker.subscriber(
        'user.event',
        group_id='presence_service',
        auto_offset_reset='earliest'
    )
async def user_event(data: UserEvent):
    event = data.event_type
    data = data.data
    logger.info(f"Получено уведомление о собынии в сервисе пользователей {event}")
    if event == 'UserDeactivated':
        await chat_service.delete_user(data.id)

@broker.subscriber(
        'chat.events',
        group_id='presence_service',
        auto_offset_reset='earliest' 
    )
async def chat_event(data: ChatEvent):
    data: ChatEvent = TypeAdapter(ChatEvent).validate_python(data)
    event = data.event_type
    data = data.data
    logger.info(f"Получено уведомление о собынии в сервисе чатов {event}")
    if event == "ChatCreated" or event == "ChatUpdated":
        await chat_service.insert(
            chat_id=data.id,
            members=data.members
        )
    elif event == 'ChatDeleted':
        await chat_service.delete_chat(data.id)
