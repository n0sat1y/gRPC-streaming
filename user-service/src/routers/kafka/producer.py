from faststream.kafka import KafkaBroker
from loguru import logger

from src.schemas.user import *

class KafkaPublisher:
    def __init__(
        self,
        broker: KafkaBroker,
        topic = 'user.event'
    ):
        self.broker = broker
        self.topic = topic

    async def create(self, data: UserData) -> None:
        event_data = UserCreatedEvent(data=data)
        await self.broker.publish(
            message=event_data,
            topic=self.topic
        )
        logger.info(f"Уведомление о создании пользователя {data.id} отправлено")

    async def update(self, data: UserData) -> None:
        event_data = UserUpdatedEvent(data=data)
        await self.broker.publish(
            message=event_data,
            topic=self.topic
        )
        logger.info(f"Уведомление об обновлении пользователя {data.id} отправлено")

    async def delete(self, data: UserIdSchema) -> None:
        event_data = UserDeactivateEvent(data=data)
        await self.broker.publish(
            message=event_data,
            topic=self.topic
        )
        logger.info(f'Отправлено уведомление об удалении пользователя {data.id}')
