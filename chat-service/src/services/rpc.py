import grpc
from loguru import logger

from src.core.config import settings
from protos import user_pb2_grpc, user_pb2
from contextlib import asynccontextmanager

class RpcUserService:
    def __init__(self):
        self.connection_url = f"{settings.GRPC_HOST}:{settings.GRPC_USER_PORT}"

    @asynccontextmanager
    async def get_stub(self):
        async with grpc.aio.insecure_channel(self.connection_url) as channel:
            stub = user_pb2_grpc.UserStub(channel)
            yield stub

    async def get_multiple(self, ids: list):
        async with self.get_stub() as stub:
            request = user_pb2.GetMultipleUsersRequest(ids=ids)
            response = await stub.GetMultipleUsers(request)

        logger.info(f'Получены пользователи: {response.users}')
        return response

    
