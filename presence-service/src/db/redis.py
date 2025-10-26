import redis.asyncio as redis

from src.core.config import settings


redis = redis.from_url(settings.REDIS_URL)

