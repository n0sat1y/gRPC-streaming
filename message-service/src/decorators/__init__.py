from functools import wraps

import grpc
from loguru import logger

from src.exceptions import AppException


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
