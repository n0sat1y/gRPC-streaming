from faststream.kafka import KafkaBroker
from loguru import logger
from src.core.config import settings

from src.services.user import UserService
from src.schemas.user import IncomingUserEvent
from src.services.chat import ChatService
from src.schemas.chat import ChatEvent
from src.services.message import *

broker = KafkaBroker(f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}")
user_service = UserService()
chat_service = ChatService()
message_service = MessageService()

@broker.subscriber(
        'user.event',
        group_id='message_service',
        auto_offset_reset='earliest'
    )
async def user_event(data: IncomingUserEvent):
    event = data.event_type
    data = data.data
    logger.info(f"Получено уведомление о собынии в сервисе пользователей {event}")
    if event in ("UserCreated", "UserUpdated"):
        await user_service.create(data)
    elif event == 'UserDeactivated':
        await user_service.deactivate(data)

@broker.subscriber(
        'chat.events',
        group_id='message_service',
        auto_offset_reset='earliest' 
    )
async def chat_event(data: ChatEvent):
    event = data.event_type
    data = data.data
    logger.info(f"Получено уведомление о собынии в сервисе чатов {event}")
    if event == "ChatCreated" or event == "ChatUpdated":
        await chat_service.upsert(data)
    elif event == 'ChatDeleted':
        await chat_service.delete(data)
        await message_service.delete_chat_messages(data.id)
    
    
@broker.subscriber(
    'api_gateway.mark_as_read',
    group_id='message_service',
    auto_offset_reset='earliest' 
)
async def handle_readed_messages(data: ApiGatewayReadEvent):
    await message_service.mark_as_read(
        chat_id=data.chat_id,
        user_id=data.user_id,
        message_id=data.last_read_message_id,
        broker=broker
    )
    logger.info(f"{data}")
    

