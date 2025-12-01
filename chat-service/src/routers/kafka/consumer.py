from loguru import logger

from src.schemas.user import UserEvent
from src.schemas.chat import ApiGatewayReadEvent
from src.schemas.message import MessageEvent
from src.routers.kafka import broker
from src.core.deps import user_service, chat_service


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

@broker.subscriber(
    'api_gateway.mark_as_read',
    group_id='chat_service',
    auto_offset_reset='earliest' 
)
async def handle_readed_messages(data: ApiGatewayReadEvent):
    await chat_service.update_last_read_message(
        chat_id=data.chat_id,
        user_id=data.user_id,
        last_read_message_id=data.last_read_message_id
    )
    logger.info(f"{data}")
    
