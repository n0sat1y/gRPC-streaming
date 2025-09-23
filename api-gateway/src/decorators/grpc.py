from functools import wraps
from typing import Any, Callable, TypeVar, Optional
import grpc
from fastapi import HTTPException
from loguru import logger
from fastapi import status

from src.enums.status_code import CodeEnum

F = TypeVar('F', bound=Callable[..., Any])

def handle_grpc_exceptions(func: F) -> F:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except grpc.RpcError as e:
            logger.error(f"gRPC error in {func.__name__}: {e.details()}")
            raise HTTPException(
                status_code=CodeEnum.from_grpc_code(e.code()), 
                detail=e.details()
            )
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
        
    return wrapper
