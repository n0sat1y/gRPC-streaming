from contextlib import asynccontextmanager

import grpc
from google.protobuf.json_format import MessageToDict
from loguru import logger

from protos import presence_pb2, presence_pb2_grpc
from src.core.config import settings
from src.schemas.events.presence import (MultipleUsersStatuses, UserStatus,
                                         UserStatusWithId)
from src.utils.decorators.grpc import handle_grpc_exceptions


class RpcPresenceService:
    def __init__(self, stub: presence_pb2_grpc.PresenceStub):
        self.stub = stub

    @handle_grpc_exceptions()
    async def set_online(self, user_id: int, ttl: int | None = None):
        request = presence_pb2.SetOnlineRequest(id=user_id, ttl=ttl)
        await self.stub.SetOnline(request)
        logger.info(f"Пользователь {user_id} в сети")

    @handle_grpc_exceptions()
    async def set_offline(self, user_id: int):
        request = presence_pb2.Id(id=user_id)
        await self.stub.SetOffline(request)
        logger.info(f"Пользователь {user_id} не в сети")

    @handle_grpc_exceptions()
    async def refresh_online(self, user_id: int, ttl: int | None = None):
        request = presence_pb2.RefreshOnlineRequest(id=user_id, ttl=ttl)
        await self.stub.RefreshOnline(request)
        logger.info(f"Обновлен онлайн статус для {user_id}")

    @handle_grpc_exceptions()
    async def get_user_status(self, user_id: int) -> UserStatus:
        request = presence_pb2.Id(id=user_id)
        response = await self.stub.GetUserStatus(request)
        logger.info(f"Получен статус для {user_id}")
        data = MessageToDict(response, preserving_proto_field_name=True)
        return UserStatus.model_validate(data)

    @handle_grpc_exceptions()
    async def get_users_statuses(self, ids: list[int]):
        request = presence_pb2.GetManyUserStatusesRequest(ids=ids)
        response = await self.stub.GetManyUserStatuses(request)
        logger.info(f"Получен статусы для нескольких пользователей")
        data = MessageToDict(response, preserving_proto_field_name=True)
        return MultipleUsersStatuses.model_validate(data)
