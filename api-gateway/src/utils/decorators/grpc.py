from functools import wraps
from typing import Any, Callable, Optional, TypeVar

import grpc
from fastapi import HTTPException, WebSocket, status
from loguru import logger

from src.utils.exceptions import GrpcError

F = TypeVar("F", bound=Callable[..., Any])


def handle_grpc_exceptions(func: F):
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except grpc.RpcError as e:
            details = e.details()
            code = e.code()

            error = GrpcError(code=code, detail=details)
            logger.error(
                f"gRPC error in {func.__name__} | Code: {code} | Details: {details}"
            )
            if code == grpc.StatusCode.UNAVAILABLE:
                error.detail = "Service unavailable"
                raise error

            if code == grpc.StatusCode.DEADLINE_EXCEEDED:
                error.detail = "Service timeout"
                raise error
            raise error
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}: {e}")
            raise GrpcError(
                code=grpc.StatusCode.UNKNOWN, detail="Internal server error"
            )

    return wrapper
