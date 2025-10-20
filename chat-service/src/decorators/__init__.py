import grpc
from functools import wraps
from loguru import logger

from src.exceptions.chat import *
from src.exceptions.user import *
from src.core.db import SessionLocal

def with_session(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with SessionLocal() as session:
            try:
                result = await func(*args, session=session, **kwargs)
                return result
            except Exception as e:
                await session.rollback()
                logger.error(f"Database Error in {func.__name__}: {e}")
                raise e
    return wrapper

def handle_exceptions(func):
    @wraps(func)
    async def wrapper(self, request, context: grpc.aio.ServicerContext):
        try:
            return await func(self, request, context)
        except (ChatNotFoundError, UserChatNotFound, 
                UsersNotFoundError, ChatMemberNotFound) as e:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                details=str(e)
            )
        except (ChatAlreadyExistsError, MembersAlreadyAdded) as e:
            await context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                details=str(e)
            ) 
        except (ChatUpdateFailed, AddMembersFailed) as e:
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details=str(e)
            )
        except Exception as e:
            logger.error(e)
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details="An internal error occured"
            )
    return wrapper
