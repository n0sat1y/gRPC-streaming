import grpc
from loguru import logger
from functools import wraps

from src.db.postgres import SessionLocal

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
        except Exception as e:
            logger.error(e)
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details="An internal error occured"
            )
    return wrapper
