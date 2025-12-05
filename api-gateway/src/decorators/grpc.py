from functools import wraps
from typing import Any, Callable, TypeVar, Optional
import grpc
from fastapi import HTTPException, WebSocket
from loguru import logger
from fastapi import status

from src.enums.status_code import CodeEnum, WsCloseCodeEnum

F = TypeVar('F', bound=Callable[..., Any])

def handle_grpc_exceptions(func: F) -> F:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except grpc.RpcError as e:
            details = e.details()
            code = e.code()

            logger.error(f"gRPC error in {func.__name__} | Code: {code} | Details: {details}")

            if code == grpc.StatusCode.UNAVAILABLE:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Service unavailable"
                )
            
            if code == grpc.StatusCode.DEADLINE_EXCEEDED:
                 raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Service timeout"
                )
            raise HTTPException(
                status_code=CodeEnum.from_grpc_code(code), 
                detail=details
            )
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
        
    return wrapper



def _find_websocket_in_args(*args: Any, **kwargs: Any) -> Optional[WebSocket]:
    for arg in args:
        if isinstance(arg, WebSocket):
            return arg
    for arg in kwargs.values():
        if isinstance(arg, WebSocket):
            return arg
    return None

def handle_websocket_grpc_exceptions(func: F) -> F:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        websocket = _find_websocket_in_args(*args, **kwargs)

        try:
            return await func(*args, **kwargs)
        
        except grpc.aio.AioRpcError as e:
            logger.error(f"gRPC error в задаче '{func.__name__}': {e.details()}")
            if websocket:
                ws_code = WsCloseCodeEnum.from_grpc_code(e.code())
                reason = e.details() or "gRPC communication error"
                try:
                    await websocket.close(code=ws_code, reason=reason)
                except RuntimeError:
                    pass
            return

        except Exception as e:
            logger.error(f"Неожиданная ошибка в задаче '{func.__name__}': {e}")
            if websocket:
                try:
                    await websocket.close(
                        code=status.WS_1011_INTERNAL_ERROR, 
                        reason="Internal Server Error"
                    )
                except RuntimeError:
                    pass
            return
            
    return wrapper
