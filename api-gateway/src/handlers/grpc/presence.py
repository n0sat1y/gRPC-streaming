import grpc
from loguru import logger
from google.protobuf.json_format import MessageToDict
from protos import presence_pb2, presence_pb2_grpc
from contextlib import asynccontextmanager

from src.core.config import settings
from src.decorators.grpc import handle_grpc_exceptions
from src.schemas.presence import UserStatus


class RpcPresenceService:
    def __init__(self):
        self.connection_url = f"{settings.GRPC_HOST}:{settings.GRPC_PRESENCE_PORT}"

    @asynccontextmanager
    async def get_stub(self):
        async with grpc.aio.insecure_channel(self.connection_url) as channel:
            stub = presence_pb2_grpc.PresenceStub(channel)
            yield stub

    @handle_grpc_exceptions
    async def set_online(self, user_id: int, ttl: int | None = None):
        async with self.get_stub() as stub:
            request = presence_pb2.SetOnlineRequest(id=user_id, ttl=ttl)
            await stub.SetOnline(request)
        logger.info(f"Пользователь {user_id} в сети")

    @handle_grpc_exceptions
    async def set_offline(self, user_id: int):
        async with self.get_stub() as stub:
            request = presence_pb2.Id(id=user_id)
            await stub.SetOffline(request)
        logger.info(f"Пользователь {user_id} не в сети")

    @handle_grpc_exceptions
    async def refresh_online(self, user_id: int, ttl: int | None = None):
        async with self.get_stub() as stub:
            request = presence_pb2.RefreshOnlineRequest(id=user_id, ttl=ttl)
            await stub.RefreshOnline(request)
        logger.info(f"Обновлен онлайн статус для {user_id}")

    @handle_grpc_exceptions
    async def get_user_status(self, user_id: int) -> UserStatus:
        async with self.get_stub() as stub:
            request = presence_pb2.Id(id=user_id)
            response = await stub.GetUserStatus(request)
        
        logger.info(f"Получен статус для {user_id}")
        data = MessageToDict(response, preserving_proto_field_name=True)
        return UserStatus.model_validate(data)
