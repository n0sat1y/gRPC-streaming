from fastapi import Depends
from faststream.kafka import KafkaRouter
from pydantic import TypeAdapter

from src.core.kafka import router
from src.dependencies import get_non_dependend_connection_manager
from src.features.message.service import MessageService
from src.schemas.events.message import *

service = MessageService(
    router=router, connection_manager=get_non_dependend_connection_manager()
)


@router.subscriber(
    "message.events", group_id="api-gateway_message", auto_offset_reset="earliest"
)
async def message_event(data: IncomingMessage):
    message: IncomingMessage = TypeAdapter(IncomingMessage).validate_python(data)
    if message.event_type == "MessageCreated":
        await service.send_message(data)
    elif message.event_type == "MessageUpdated":
        await service.update_message(data)
    elif message.event_type == "MessageDeleted":
        await service.delete_message(data)
    elif message.event_type in ["ReactionAdded", "ReactionRemoved"]:
        await service.reaction_event(data)


@router.subscriber(
    "message.read_messages",
    group_id="api-gateway_message",
    auto_offset_reset="earliest",
)
async def read_messages(data: MessagesReadEvent):
    await service.mark_as_read(data)
