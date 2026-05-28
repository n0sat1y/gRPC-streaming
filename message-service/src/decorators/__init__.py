from functools import wraps

import grpc
from loguru import logger

from src.exceptions.message import RequestIdAlreadyProcessedError
from src.core.deps import get_redis
from src.exceptions import AppException

redis = get_redis()


def handle_exceptions(func):
    @wraps(func)
    async def wrapper(self, request, context: grpc.aio.ServicerContext):
        try:
            return await func(self, request, context)
        except AppException as e:
            logger.error(e)
            await context.abort(e.status_code, e.detail)
        except Exception as e:
            logger.exception(e)
            await context.abort(grpc.StatusCode.INTERNAL, details="Internal error")

    return wrapper


def check_processed(ttl_days: int = 7):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if "request_id" in kwargs and kwargs["request_id"] is not None:
                request_id = kwargs["request_id"]
                key = f"request_id:{request_id}"

                logger.debug(
                    f"Request_id был передан в аргументах: {request_id}. Проверяем его обработку"
                )
                if await redis.get(key):
                    logger.warning(f"Данный request уже был обработан: {request_id}")
                    raise RequestIdAlreadyProcessedError(request_id)
                result = await func(*args, **kwargs)
                logger.debug("Создаем запись об обработке request")
                await redis.set(key, "Processed", ex=ttl_days * 60 * 60 * 24)
                return result
            else:
                return await func(*args, **kwargs)

        return wrapper
