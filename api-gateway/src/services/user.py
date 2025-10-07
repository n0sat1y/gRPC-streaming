import grpc
from loguru import logger
from protos import user_pb2, user_pb2_grpc
from contextlib import asynccontextmanager

from src.core.config import settings
from src.decorators.grpc import handle_grpc_exceptions


class RpcUserService:
    def __init__(self):
        self.connection_url = f"{settings.GRPC_HOST}:{settings.GRPC_USER_PORT}"

    @asynccontextmanager
    async def get_stub(self):
        async with grpc.aio.insecure_channel(self.connection_url) as channel:
            stub = user_pb2_grpc.UserStub(channel)
            yield stub

    @handle_grpc_exceptions
    async def get_user_by_id(self, user_id: int):
        async with self.get_stub() as stub:
            request = user_pb2.GetUserByIdRequest(id=user_id)
            response = await stub.GetUserById(request)

        logger.info(f'Получен пользователь: {response.username}')
        return response.username
    
    @handle_grpc_exceptions
    async def get_user_with_password(self, username: str):
        async with self.get_stub() as stub:
            request = user_pb2.GetUserWithPasswordRequest(username=username)
            response = await stub.GetUserWithPassword(request)

        logger.info(f'Получен пользователь: {response.user_id}')
        return response
    
    @handle_grpc_exceptions
    async def create_user(self, username: str, password: str):
        async with self.get_stub() as stub:
            request = user_pb2.CreateUserRequest(
                username=username, 
                password=password
            )
            response = await stub.CreateUser(request)

        logger.info(f"Пользователь создан: {response.id}")
        return response.id
    
    @handle_grpc_exceptions
    async def delete_user(self, user_id: int):
        async with self.get_stub() as stub:
            request = user_pb2.DeleteUserRequest(user_id=user_id)
            response = await stub.DeleteUser(request)

        logger.info(f'Удален пользователь: {user_id}')
        return response.status
