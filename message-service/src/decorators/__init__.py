import grpc
from functools import wraps
from loguru import logger

from src.exceptions.message import *
from src.exceptions.user import *
from src.exceptions.chat import *

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
        except (MessageNotFoundError, UserNotFoundError, ChatNotFoundError) as e:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                details=str(e)
            )
        except ReacionNotAdded as e:
            await context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                details=str(e)
            )
        except Exception as e:
            logger.error(e)
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details="An internal error occured"
            )
    return wrapper
