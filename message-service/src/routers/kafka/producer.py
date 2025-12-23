from typing import Union
from faststream.kafka import KafkaBroker
from loguru import logger

from src.schemas.message import *


class KafkaPublisher:
    def __init__(
        self,
        broker: KafkaBroker,
        topic = 'message.events'
    ):
        self.broker = broker
        self.topic = topic
        self.logger = logger

    async def _publish(
        self,
        event: Union[CreatedMessageEvent, UpdateMessageEvent, DeleteMessageEvent]
    ) -> None:
        await self.broker.publish(event, self.topic)

    async def create_message(
        self, 
        data: MessageData,
        recievers: list[int],
        request_id: str,
        sender_id: int
    ) -> None:
        self.logger.info('Публикуем событие создания сообщения в Kafka')
        return await self._publish(
            CreatedMessageEvent(
                recievers=recievers,
                data=data,
                request_id=request_id,
                sender_id=sender_id,
            )
        )

    async def update_message(
        self, 
        data: UpdateMessagePayload,
        recievers: list[int],
        request_id: str,
        sender_id: int
    ) -> None:
        self.logger.info('Публикуем событие обновления сообщения в Kafka')
        return await self._publish(
            UpdateMessageEvent(
                recievers=recievers,
                data=data,
                request_id=request_id,
                sender_id=sender_id,
            )
        )

    async def delete_message(
        self, 
        data: MessageIdPayload,
        recievers: list[int],
        request_id: str,
        sender_id: int
    ) -> None:
        self.logger.info('Публикуем событие удаления сообщения в Kafka')
        return await self._publish(
            DeleteMessageEvent(
                recievers=recievers,
                data=data,
                request_id=request_id,
                sender_id=sender_id,
            )
        )

    async def read_message(
        self, 
        data: list[SlimMessageData]
    ) -> None:
        self.logger.info('Публикуем событие чтения сообщений в Kafka')
        return await self._publish(MessagesReadEvent(data=data))

    async def add_reaction(
            self,
            data: Reaction
    ) -> None:
        self.logger.info('Публикуем событие о добавлении реакции сообщения')
        return await self._publish(ReactionEvent(
            event_type='AddReaction',
            data=data
        ))

    async def remove_reaction(
            self,
            data: Reaction
    ) -> None:
        self.logger.info('Публикуем событие об удалении реакции на сообщение')
        return await self._publish(ReactionEvent(
            event_type='RemoveReaction',
            data=data
        ))
