from google.protobuf import empty_pb2
from loguru import logger

from protos import presence_pb2, presence_pb2_grpc
from src.services.presence import PresenceService
from src.decorators import handle_exceptions
from src.routers.kafka import broker


class Presence(presence_pb2_grpc.PresenceServicer):
    def __init__(self):
        self.service = PresenceService()
        self.broker = broker

    @handle_exceptions
    async def SetOnline(self, request, context):
        logger.info(f"Поступил запрос на установку статуса online для пользователя {request.id}")
        ttl = request.ttl if request.ttl else 60
        await self.service.set_online(request.id, self.broker, ttl)
        return empty_pb2.Empty()
    
    @handle_exceptions
    async def SetOffline(self, request, context):
        logger.info(f"Поступил запрос на установку статуса offline для пользователя {request.id}")
        await self.service.set_offline(request.id, self.broker)
        return empty_pb2.Empty()
    
    @handle_exceptions
    async def RefreshOnline(self, request, context):
        logger.info(f"Поступил запрос на обновление статуса online для пользователя {request.id}")
        ttl = request.ttl if request.ttl else 60
        await self.service.refresh_user_status(request.id, broker, ttl)
        return empty_pb2.Empty()
    
    @handle_exceptions
    async def GetUserStatus(self, request, context):
        logger.info(f"Поступил запрос на получение статуса для пользователя {request.id}")
        status = await self.service.get_user_status(request.id)
        return presence_pb2.UserStatus(status=status)
    
    @handle_exceptions
    async def GetManyUserStatuses(self, request, context):
        logger.info(f"Поступил запрос на получение статусов для пользователей")
        ids = list(request.ids) 
        result = await self.service.get_multiple_statuses(ids)

        status_objects = [
            presence_pb2.StatusWithId(id=user_id, status=status) 
            for user_id, status in result.items()
        ]

        return presence_pb2.UserStatusesResponse(statuses=status_objects)
