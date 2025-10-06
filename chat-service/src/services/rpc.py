import grpc
from loguru import logger

from src.core.config import settings
from protos import user_pb2_grpc, user_pb2

class RpcService:
    def __init__(self):
        self.user_connection_url = f"{settings.GRPC_HOST}:{settings.GRPC_USER_PORT}"
