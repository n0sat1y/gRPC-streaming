import enum
from grpc import StatusCode
from fastapi import status


class CodeEnum(enum.Enum):
    OK = status.HTTP_200_OK
    INVALID_ARGUMENT = status.HTTP_400_BAD_REQUEST
    FAILED_PRECONDITION = status.HTTP_400_BAD_REQUEST
    OUT_OF_RANGE = status.HTTP_400_BAD_REQUEST
    UNAUTHENTICATED = status.HTTP_401_UNAUTHORIZED
    PERMISSION_DENIED = status.HTTP_403_FORBIDDEN
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    ABORTED = status.HTTP_409_CONFLICT
    ALREADY_EXISTS = status.HTTP_409_CONFLICT
    RESOURCE_EXHAUSTED = status.HTTP_429_TOO_MANY_REQUESTS
    CANCELLED = 499
    UNKNOWN = status.HTTP_500_INTERNAL_SERVER_ERROR
    INTERNAL = status.HTTP_500_INTERNAL_SERVER_ERROR
    DATA_LOSS = status.HTTP_500_INTERNAL_SERVER_ERROR
    UNIMPLEMENTED = status.HTTP_501_NOT_IMPLEMENTED
    UNAVAILABLE = status.HTTP_503_SERVICE_UNAVAILABLE
    DEADLINE_EXCEEDED = status.HTTP_504_GATEWAY_TIMEOUT
    
    @classmethod
    def from_grpc_code(cls, grpc_code: StatusCode) -> int:
        """Конвертирует gRPC StatusCode в HTTP код"""
        mapping = {
            StatusCode.OK: cls.OK.value,
            StatusCode.CANCELLED: cls.CANCELLED.value,
            StatusCode.UNKNOWN: cls.UNKNOWN.value,
            StatusCode.INVALID_ARGUMENT: cls.INVALID_ARGUMENT.value,
            StatusCode.DEADLINE_EXCEEDED: cls.DEADLINE_EXCEEDED.value,
            StatusCode.NOT_FOUND: cls.NOT_FOUND.value,
            StatusCode.ALREADY_EXISTS: cls.ALREADY_EXISTS.value,
            StatusCode.PERMISSION_DENIED: cls.PERMISSION_DENIED.value,
            StatusCode.UNAUTHENTICATED: cls.UNAUTHENTICATED.value,
            StatusCode.RESOURCE_EXHAUSTED: cls.RESOURCE_EXHAUSTED.value,
            StatusCode.FAILED_PRECONDITION: cls.FAILED_PRECONDITION.value,
            StatusCode.ABORTED: cls.ABORTED.value,
            StatusCode.OUT_OF_RANGE: cls.OUT_OF_RANGE.value,
            StatusCode.UNIMPLEMENTED: cls.UNIMPLEMENTED.value,
            StatusCode.INTERNAL: cls.INTERNAL.value,
            StatusCode.UNAVAILABLE: cls.UNAVAILABLE.value,
            StatusCode.DATA_LOSS: cls.DATA_LOSS.value,
        }
        return mapping.get(grpc_code, cls.INTERNAL.value)
    

class WsCloseCodeEnum(enum.Enum):
    """
    Перечисление кодов закрытия WebSocket.
    Основные коды согласно RFC 6455.
    """
    NORMAL = status.WS_1000_NORMAL_CLOSURE
    POLICY_VIOLATION = status.WS_1008_POLICY_VIOLATION 
    INTERNAL_ERROR = status.WS_1011_INTERNAL_ERROR
    TRY_AGAIN_LATER = status.WS_1013_TRY_AGAIN_LATER

    @classmethod
    def from_grpc_code(cls, grpc_code: StatusCode) -> int:
        """
        Конвертирует gRPC StatusCode в WebSocket Close Code.
        Происходит группировка детальных gRPC статусов в общие категории WS.
        """
        mapping = {
            StatusCode.OK: cls.NORMAL.value,
            StatusCode.CANCELLED: cls.NORMAL.value, 
            StatusCode.INVALID_ARGUMENT: cls.POLICY_VIOLATION.value,
            StatusCode.NOT_FOUND: cls.POLICY_VIOLATION.value,
            StatusCode.OUT_OF_RANGE: cls.POLICY_VIOLATION.value,
            StatusCode.FAILED_PRECONDITION: cls.POLICY_VIOLATION.value,
            StatusCode.ALREADY_EXISTS: cls.POLICY_VIOLATION.value,
            StatusCode.PERMISSION_DENIED: cls.POLICY_VIOLATION.value,
            StatusCode.UNAUTHENTICATED: cls.POLICY_VIOLATION.value,
            StatusCode.RESOURCE_EXHAUSTED: cls.TRY_AGAIN_LATER.value,
            StatusCode.UNAVAILABLE: cls.TRY_AGAIN_LATER.value,
            StatusCode.DEADLINE_EXCEEDED: cls.TRY_AGAIN_LATER.value,
            StatusCode.UNKNOWN: cls.INTERNAL_ERROR.value,
            StatusCode.ABORTED: cls.INTERNAL_ERROR.value,
            StatusCode.UNIMPLEMENTED: cls.INTERNAL_ERROR.value,
            StatusCode.INTERNAL: cls.INTERNAL_ERROR.value,
            StatusCode.DATA_LOSS: cls.INTERNAL_ERROR.value,
        }
        return mapping.get(grpc_code, cls.INTERNAL_ERROR.value)
