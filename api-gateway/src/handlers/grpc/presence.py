import grpc
from loguru import logger
from google.protobuf.json_format import MessageToDict
from protos import presence_pb2, presence_pb2_grpc
from contextlib import asynccontextmanager

from src.core.config import settings
from src.decorators.grpc import handle_grpc_exceptions
from src.schemas.presence import UserStatus, MultipleUsersStatuses, UserStatusWithId
from protos import presence_pb2_grpc


class RpcPresenceService:
    def __init__(self, stub: presence_pb2_grpc.PresenceStub):
        self.stub = stub

    @handle_grpc_exceptions
    async def set_online(self, user_id: int, ttl: int | None = None):
        try:
            request = presence_pb2.SetOnlineRequest(id=user_id, ttl=ttl)
            await self.stub.SetOnline(request)
            logger.info(f"Пользователь {user_id} в сети")
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                return
            raise e

    @handle_grpc_exceptions
    async def set_offline(self, user_id: int):
        try:
            request = presence_pb2.Id(id=user_id)
            await self.stub.SetOffline(request)
            logger.info(f"Пользователь {user_id} не в сети")
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                return
            raise e

    @handle_grpc_exceptions
    async def refresh_online(self, user_id: int, ttl: int | None = None):
        try:
            request = presence_pb2.RefreshOnlineRequest(id=user_id, ttl=ttl)
            await self.stub.RefreshOnline(request)
            logger.info(f"Обновлен онлайн статус для {user_id}")
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                return
            raise e

    @handle_grpc_exceptions
    async def get_user_status(self, user_id: int) -> UserStatus:
        try:
            request = presence_pb2.Id(id=user_id)
            response = await self.stub.GetUserStatus(request)
            logger.info(f"Получен статус для {user_id}")
            data = MessageToDict(response, preserving_proto_field_name=True)
            return UserStatus.model_validate(data)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                return UserStatus(status='offline')
            raise e
        
    @handle_grpc_exceptions
    async def get_users_statuses(self, ids: list[int]):
        try:
            request = presence_pb2.GetManyUserStatusesRequest(ids=ids)
            response = await self.stub.GetManyUserStatuses(request)
            logger.info(f"Получен статусы для нескольких пользователей")
            data = MessageToDict(response, preserving_proto_field_name=True)
            return MultipleUsersStatuses.model_validate(data)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                return MultipleUsersStatuses(statuses=[UserStatusWithId(id=x, status='offline') for x in ids])
            raise e
