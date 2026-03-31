import grpc


class GrpcError(Exception):
    def __init__(self, code: grpc.StatusCode, detail: str | None) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"Error: {self.code} - {self.detail}")
