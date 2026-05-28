from typing import Any, Optional, Union
from datetime import timedelta
from redis.asyncio import Redis
from redis.typing import ResponseT


class RedisRepository:
    def __init__(self, redis_client: Redis) -> None:
        self.redis = redis_client

    async def get(self, key: str) -> ResponseT:
        return await self.redis.get(key)

    async def set(
        self, key: str, value: Any, ex: Optional[Union[int, timedelta]]
    ) -> Any:
        return await self.redis.set(name=key, value=value, ex=ex)

