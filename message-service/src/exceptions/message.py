import grpc

from src.exceptions import AccessDeniedError, AppException, NotFoundError


class MessageNotFoundError(NotFoundError):
    def __init__(self, message_id: str):
        self.message_id = message_id
        super().__init__(f"Message not found: {self.message_id}")


class ReacionNotAdded(AppException):
    status_code = grpc.StatusCode.ALREADY_EXISTS

    def __init__(self):
        super().__init__(f"Reaction already added")


class ForwardMessageFailed(AppException):
    status_code = grpc.StatusCode.ABORTED

    def __init__(self, detail=None) -> None:
        super().__init__(f"Failde to forward messages, detail={detail}")
