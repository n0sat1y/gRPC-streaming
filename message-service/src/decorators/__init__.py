import grpc
from functools import wraps
from loguru import logger

from src.exceptions.message import *

def handle_exceptions(func):
    @wraps(func)
    async def wrapper(self, request, context: grpc.aio.ServicerContext):
        try:
            return await func(self, request, context)
        except DataLossError as e:
            await context.abort(
                grpc.StatusCode.DATA_LOSS,
                details=str(e)
            )
        except MessageNotFoundError as e:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                details=str(e)
            )
        except Exception as e:
            logger.error(e)
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details="An internal error occured"
            )
    return wrapper
