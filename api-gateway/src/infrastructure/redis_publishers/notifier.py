import asyncio
import json

from loguru import logger
from redis.asyncio import Redis


class RedisNotifier:
    def __init__(self, redis_client: Redis) -> None:
        self.redis_client = redis_client

    def _get_notification_channel(self, user_id: int):
        return f"user_notifications:{user_id}"

    async def publish_to_user(self, user_id: int, data: dict):
        channel_name = self._get_notification_channel(user_id)
        json_data = json.dumps(data)
        await self.redis_client.publish(channel_name, json_data)
        logger.info(f"Отправлено сообщение пользователю {user_id}")

    async def broadcast(self, recievers: list[int], data: dict):
        coros = []
        for reciever in recievers:
            coros.append(self.publish_to_user(reciever, data))
        asyncio.gather(*coros)
