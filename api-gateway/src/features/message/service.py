from collections import defaultdict
from typing import Union

from faststream.kafka import KafkaRouter
from loguru import logger
from pydantic import TypeAdapter

from src.infrastructure.redis_publishers.notifier import RedisNotifier
from src.schemas.events.message import (AddReactionEvent,
                                        CreatedManyMessagesEvent,
                                        CreatedMessageEvent,
                                        DeleteMessageEvent, MessagesReadEvent,
                                        RemoveReactionEvent,
                                        UpdateMessageEvent)


class MessageService:
    def __init__(self, router: KafkaRouter, redis_publisher: RedisNotifier):
        self.router = router
        self.read_message_pub = self.router.publisher("api_gateway.messages_read")
        self.redis_publisher = redis_publisher

    async def send_message(self, data: CreatedMessageEvent):
        logger.info(f"Пришло сообщение {data.event_type}")
        # payload = data.data.model_dump(mode="json")
        payload = data.data
        sender_id = data.sender_id
        recievers = [x for x in data.recievers if x != sender_id]

        await self.redis_publisher.broadcast(
            recievers, {"event_type": "new_message", "payload": payload}
        )

        personal_payload = payload.copy()
        await self.redis_publisher.publish_to_user(
            user_id=sender_id,
            data={
                "event_type": "message_sended",
                "payload": personal_payload,
                "request_id": data.request_id,
            },
        )

    async def forward_messages(self, data: CreatedManyMessagesEvent):
        logger.info(f"Пришло сообщение {data.event_type}")
        # payload = data.data.model_dump(mode="json")
        payload = data.data
        sender_id = data.sender_id
        recievers = [x for x in data.recievers if x != sender_id]

        await self.redis_publisher.broadcast(
            recievers, {"event_type": "new_messages", "payload": payload}
        )

        personal_payload = payload.copy()
        await self.redis_publisher.publish_to_user(
            user_id=sender_id,
            data={
                "event_type": "messages_sended",
                "payload": personal_payload,
                "request_id": data.request_id,
            },
        )

    async def update_message(self, data: UpdateMessageEvent):
        logger.info(f"Пришло сообщение {data.event_type}")
        payload = data.data.model_dump(mode="json")
        sender_id = data.sender_id
        recievers = [x for x in data.recievers if x != sender_id]

        await self.redis_publisher.broadcast(
            recievers, {"event_type": "update_message", "payload": payload}
        )

        await self.redis_publisher.publish_to_user(
            user_id=sender_id,
            data={
                "event_type": "message_updated",
                "payload": payload,
                "request_id": data.request_id,
            },
        )

    async def delete_message(self, data: DeleteMessageEvent):
        logger.info(f"Пришло сообщение {data.event_type}")
        payload = data.data.model_dump(mode="json")
        sender_id = data.sender_id
        recievers = [x for x in data.recievers if x != sender_id]

        await self.redis_publisher.broadcast(
            recievers, {"event_type": "delete_message", "payload": payload}
        )

        await self.redis_publisher.publish_to_user(
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

        logger.info(data_payload)

        for message in data_payload:
            message_id = message.id
            author = message.sender_id
            await self.redis_publisher.publish_to_user(
                user_id=author,
                data={
                    "event_type": "read_cursor_updated",
                    "payload": {"cursor_id": message_id},
                },
            )

    async def reaction_event(self, data: Union[AddReactionEvent, RemoveReactionEvent]):
        logger.info(f"Пришло сообщение: {data.event_type}")
        sender_id = data.sender_id
        recievers = data.recievers
        payload = data.data.model_dump(mode="json")

        logger.info(payload)
        await self.redis_publisher.broadcast(
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
