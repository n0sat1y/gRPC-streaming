import asyncio
from loguru import logger
from faststream.kafka import KafkaBroker

from src.db.redis import redis
from src.services.presence import PresenceService


class TtlListener:
    def __init__(self, broker: KafkaBroker):
        self.redis = redis
        self.pubsub = self.redis.pubsub()
        self.presence_service = PresenceService()
        self.broker = broker

    async def listen(self):
        logger.info("Запуск прослушивания истечения срока действия ключа Redis")
        await self.pubsub.psubscribe("__keyevent@0__:expired")
        while True:
            try:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message['type'] == 'pmessage':
                    key = message['data'].decode('utf-8')
                    if key.startswith("user_status:"):
                        user_id = int(key.split(":")[1])
                        logger.info(f"Срок действия ключа истек для пользователя {user_id}")
                        await self.presence_service.set_offline(user_id, self.broker)
                await asyncio.sleep(0.01)
            except asyncio.CancelledError:
                logger.info("Прослушиватель TTL остановлен")
                break
            except Exception as e:
                logger.error(f"Ошибка в прослушивателе TTL: {e}")

