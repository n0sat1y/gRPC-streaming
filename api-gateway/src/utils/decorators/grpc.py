import asyncio
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

import grpc
from fastapi import HTTPException, WebSocket, status
from loguru import logger

from src.utils.exceptions import GrpcError

unretryable_exceptions = [
    grpc.StatusCode.INVALID_ARGUMENT,
    grpc.StatusCode.NOT_FOUND,
    grpc.StatusCode.PERMISSION_DENIED,
    grpc.StatusCode.UNAUTHENTICATED,
    grpc.StatusCode.INTERNAL,
    grpc.StatusCode.ALREADY_EXISTS,
    grpc.StatusCode.FAILED_PRECONDITION,
    grpc.StatusCode.UNIMPLEMENTED,
    grpc.StatusCode.CANCELLED,
    grpc.StatusCode.ABORTED,
]


def handle_grpc_exceptions(
    attempt_count: int = 10,
    base_delay: float = 0.1,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for i in range(attempt_count):
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

                    if code == grpc.StatusCode.DEADLINE_EXCEEDED:
                        error.detail = "Service timeout"
                    last_exception = error

                    if e.code() in unretryable_exceptions:
                        raise error

                    if i == attempt_count - 1:
                        break

                    delay = min(base_delay * (exponential_base ** (i + 1)), max_delay)
                    logger.warning(
                        f"Attempt {i + 1}/{attempt_count} failed for {func.__name__}"
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                except Exception as e:
                    logger.exception(f"Unexpected error in {func.__name__}: {e}")
                    raise GrpcError(
                        code=grpc.StatusCode.UNKNOWN, detail="Internal server error"
                    )
            raise last_exception

        return wrapper

    return decorator
