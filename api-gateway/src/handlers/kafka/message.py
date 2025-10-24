from loguru import logger
from faststream.kafka import KafkaRouter
from pydantic import TypeAdapter

from src.services.connection import manager
from src.schemas.message import *
from src.services.message import MessageService

router = KafkaRouter()
service = MessageService(router)

@router.subscriber(
    'message.event',
    group_id='api-gateway',
    auto_offset_reset='earliest'
)
async def message_event(data: IncomingMessage):
    message: IncomingMessage = TypeAdapter(IncomingMessage).validate_python(data)
    if message.event_type == 'MessageCreated':
        await service.send_message(data)
    elif message.event_type == 'MessageUpdated':
        await service.update_message(data)
    elif message.event_type == 'MessageDeleted':
        await service.delete_message(data)

@router.subscriber(
    'message.read_messages',
    group_id='api-gateway',
    auto_offset_reset='earliest'
)
async def read_messages(data: MessagesReadEvent):
    print('YYYEEEEEYYY')
    await service.mark_as_read(data)


