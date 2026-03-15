from collections import defaultdict
from typing import Union

from faststream.kafka import KafkaRouter
from loguru import logger
from pydantic import TypeAdapter

from src.infrastructure.websocket.manager import ConnectionManager
from src.schemas.events.message import (AddReactionEvent, CreatedMessageEvent,
                                        DeleteMessageEvent, MessagesReadEvent,
                                        RemoveReactionEvent,
                                        UpdateMessageEvent)


class MessageService:
    def __init__(self, router: KafkaRouter, connection_manager: ConnectionManager):
        self.router = router
        self.connection_manager = connection_manager
        self.read_message_pub = self.router.publisher("api_gateway.messages_read")

    async def send_message(self, data: CreatedMessageEvent):
        logger.info(f"Пришло сообщение {data.event_type}")
        data_dict = data.model_dump(mode="json")
        sender_id = data.sender_id
        recievers = [x for x in data.recievers if x != sender_id]
        payload = data_dict["data"]

        await self.connection_manager.broadcast(
            recievers, {"event_type": "new_message", "payload": payload}
        )

        payload.pop("sender")
        await self.connection_manager.send_personal_message(
            user_id=sender_id,
            data={
                "event_type": "message_sended",
                "payload": payload,
                "request_id": data.request_id,
            },
        )

    async def update_message(self, data: UpdateMessageEvent):
        logger.info(f"Пришло сообщение {data.event_type}")
        data_dict = data.model_dump(mode="json")
        sender_id = data.sender_id
        recievers = [x for x in data.recievers if x != sender_id]
        payload = data_dict["data"]

        await self.connection_manager.broadcast(
            recievers, {"event_type": "update_message", "payload": payload}
        )

        await self.connection_manager.send_personal_message(
            user_id=sender_id,
            data={
                "event_type": "message_updated",
                "payload": payload,
                "request_id": data.request_id,
            },
        )

    async def delete_message(self, data: DeleteMessageEvent):
        logger.info(f"Пришло сообщение {data.event_type}")
        data_dict = data.model_dump(mode="json")
        sender_id = data.sender_id
        recievers = [x for x in data.recievers if x != sender_id]
        payload = data_dict["data"]

        await self.connection_manager.broadcast(
            recievers, {"event_type": "delete_message", "payload": payload}
        )

        await self.connection_manager.send_personal_message(
            user_id=sender_id,
            data={
                "event_type": "message_deleted",
                "payload": payload,
                "request_id": data.request_id,
            },
        )

    async def mark_as_read(self, data: MessagesReadEvent):
        logger.info(f"Пришло сообщение {data.event_type}")
        data_payload = data.data
        messages_list = data_payload

        messages_sorted_by_sender = defaultdict(list)
        for message in messages_list:
            messages_sorted_by_sender[message.sender_id].append(message.id)

        for key, value in messages_sorted_by_sender.items():
            await self.connection_manager.send_personal_message(
                user_id=key,
                data={
                    "event_type": "read_messages",
                    "payload": value,
                },
            )

    async def reaction_event(self, data: Union[AddReactionEvent, RemoveReactionEvent]):
        logger.info(f"Пришло сообщение: {data.event_type}")
        sender_id = data.sender_id
        recievers = data.recievers
        payload = data.data.model_dump(mode="json")

        await self.connection_manager.broadcast(
            recievers,
            {
                "event_type": (
                    "add_reaction"
                    if data.event_type == "ReactionAdded"
                    else "remove_reaction"
                ),
                "payload": payload,
                "sender_id": sender_id,
            },
        )
