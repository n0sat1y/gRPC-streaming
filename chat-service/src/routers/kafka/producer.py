from faststream.kafka import KafkaBroker
from loguru import logger

from src.schemas.chat import (
    CreateChatEvent, UpdateChatEvent, 
    DeleteChatEvent, ChatDataBase,
    ChatIdBase
)


class KafkaPublisher:
    def __init__(
        self,
        broker: KafkaBroker,
        topic = 'chat.events'
    ):
        self.broker = broker
        self.topic = topic
        self.logger = logger

    async def create(self, data: ChatDataBase) -> None:
        event_data = CreateChatEvent(data=data)
        await self.broker.publish(
            message=event_data,
            topic=self.topic
        )
        self.logger.info(f"Уведомление о создании чата {data.id} отправлено")

    async def update(self, data: ChatDataBase) -> None:
        event_data = UpdateChatEvent(data=data)
        await self.broker.publish(
            message=event_data,
            topic=self.topic
        )
        self.logger.info(f"Уведомление об обновлении {data.id} отправлено")

    async def delete(self, chat_id: int) -> None:
        data = ChatIdBase(id=chat_id)
        event_data = DeleteChatEvent(data=data)
        await self.broker.publish(
            message=event_data,
            topic=self.topic
        )
        self.logger.info(f"Уведомление об удалении {data.id} отправлено")
