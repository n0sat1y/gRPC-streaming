from loguru import logger
from faststream.kafka import KafkaBroker

from src.db.redis import redis
from src.services.chat import ChatService
from src.schemas.presence import PresenceEvent

class PresenceService:
    def __init__(self):
        self.redis = redis
        self.chat_service = ChatService()

    async def set_online(self, user_id: int, broker: KafkaBroker, ttl: int = 60):
        try:
            logger.info(f"Устанавливаем online-сатус для пользователя {user_id}")
            key = f"user_status:{user_id}"
            await self.redis.set(key, 'online', ex=ttl)
        except Exception as e:
            logger.error(f"{e}")

        logger.info(f"Пользователь {user_id} установлен как онлайн с TTL {ttl}с")

        recievers = await self.chat_service.get_relations(user_id)
        print(recievers)
        if recievers:
            await broker.publish(
                PresenceEvent(
                    user_id=user_id,
                    status='online',
                    recievers=recievers
                ), 'presence.status'
            )
            logger.info(f"Уведомление об изменении статуса пользователя {user_id} отправлено")


    async def refresh_user_status(self, user_id: int, ttl_seconds: int = 60):
        key = f"user_status:{user_id}"
        await self.redis.expire(key, ttl_seconds)
        print(f"TTL пользователя {user_id} обновлен до {ttl_seconds}с")

    
    async def set_offline(self, user_id: int, broker: KafkaBroker):
        logger.info(f"Удаляем online-сатус для пользователя {user_id}")
        key = f"user_status:{user_id}"
        await self.redis.delete(key)

        recievers = await self.chat_service.get_relations(user_id)
        print(recievers)
        if recievers:
            await broker.publish(
                PresenceEvent(
                    user_id=user_id,
                    status='offline',
                    recievers=recievers
                ), 'presence.status'
            )
            logger.info(f"Уведомление об изменении статуса пользователя {user_id} отправлено")

        logger.info(f"Пользователь {user_id} теперь оффлайн")

    async def get_user_status(self, user_id: int) -> str:
        key = f"user_status:{user_id}"
        status = await self.redis.get(key)
        if status:
            return status.decode('utf-8')
        return "offline"
