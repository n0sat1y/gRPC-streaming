import grpc
from google.protobuf.json_format import MessageToDict
from loguru import logger
from protos import user_pb2, user_pb2_grpc
from contextlib import asynccontextmanager
from google.protobuf.json_format import MessageToDict

from src.core.config import settings
from src.decorators.grpc import handle_grpc_exceptions
from src.schemas.user import UpdateUserDataSchema, UserData, UserIdSchema

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
            request = user_pb2.UserId(id=user_id)
            response = await stub.GetUserById(request)

        logger.info(f'Получен пользователь: {response.username}')
        response = MessageToDict(response, preserving_proto_field_name=True)
        return UserData(**response)
    
    @handle_grpc_exceptions
    async def get_user_with_password(self, username: str):
        async with self.get_stub() as stub:
            request = user_pb2.UsernameRequest(username=username)
            response = await stub.GetUserByUsernameWithPassword(request)

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
        return UserIdSchema(id=response.id)
    
    @handle_grpc_exceptions
    async def update_user(self, id: int, data: UpdateUserDataSchema):
        async with self.get_stub() as stub:
            request = user_pb2.UpdateUserRequest(
                id=id,
                **data.model_dump()
            )
            response = await stub.UpdateUser(request)

        logger.info(f"Пользователь обновлен: {response.id}")
        return UserIdSchema(id=response.id)
    
    @handle_grpc_exceptions
    async def delete_user(self, user_id: int):
        async with self.get_stub() as stub:
            request = user_pb2.UserId(id=user_id)
            response = await stub.DeleteUser(request)

        logger.info(f'Удален пользователь: {user_id}')
        return response.status
