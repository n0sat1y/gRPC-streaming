import grpc


class AppException(Exception):
    status_code = grpc.StatusCode.INTERNAL
    detail = "In internal error occured"

    def __init__(self, detail=None) -> None:
        if detail:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(AppException):
    status_code = grpc.StatusCode.NOT_FOUND


class DataLossError(AppException):
    status_code = grpc.StatusCode.DATA_LOSS

    def __init__(self, err: str):
        self.err = err
        super().__init__(f"Wrong data: {self.err}")


class AccessDeniedError(AppException):
    status_code = grpc.StatusCode.PERMISSION_DENIED

    def __init__(self) -> None:
        super().__init__("Access denied")
