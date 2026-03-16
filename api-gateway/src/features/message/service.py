from collections import defaultdict
from typing import Union

from faststream.kafka import KafkaRouter
from loguru import logger
from pydantic import TypeAdapter

from src.infrastructure.redis_publishers.notifier import RedisNotifier
from src.schemas.events.message import (AddReactionEvent, CreatedMessageEvent,
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
        payload = data.data.model_dump(mode="json")
        sender_id = data.sender_id
        recievers = [x for x in data.recievers if x != sender_id]

        await self.redis_publisher.broadcast(
            recievers, {"event_type": "new_message", "payload": payload}
        )

        personal_payload = payload.copy()
        personal_payload.pop("sender")
        await self.redis_publisher.publish_to_user(
            user_id=sender_id,
            data={
                "event_type": "message_sended",
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
        messages_list = data_payload

        messages_sorted_by_sender = defaultdict(list)
        for message in messages_list:
            messages_sorted_by_sender[message.sender_id].append(message.id)

        logger.debug(messages_sorted_by_sender)

        for key, value in messages_sorted_by_sender.items():
            await self.redis_publisher.publish_to_user(
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
