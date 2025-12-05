import grpc
from typing import Optional
from protos import (
    chat_pb2_grpc,
    message_pb2_grpc,
    presence_pb2_grpc,
    user_pb2_grpc
)
from src.core.config import settings


class GRPCService:
    def __init__(self):
        self.chat: Optional[chat_pb2_grpc.ChatStub] = None
        self.message: Optional[message_pb2_grpc.MessageServiceStub] = None
        self.user: Optional[user_pb2_grpc.UserStub] = None
        self.presence: Optional[presence_pb2_grpc.PresenceStub] = None

        self.chat_channel = None
        self.message_channel = None
        self.presence_channel = None
        self.user_channel = None
    
    async def start(self):
        self.chat_channel = grpc.aio.insecure_channel(
            f"{settings.GRPC_HOST}:{settings.GRPC_CHAT_PORT}"
        )
        self.chat = chat_pb2_grpc.ChatStub(self.chat_channel)

        self.user_channel = grpc.aio.insecure_channel(
            f"{settings.GRPC_HOST}:{settings.GRPC_USER_PORT}"
        )
        self.user = user_pb2_grpc.UserStub(self.user_channel)

        self.presence_channel = grpc.aio.insecure_channel(
            f"{settings.GRPC_HOST}:{settings.GRPC_PRESENCE_PORT}"
        )
        self.presence = presence_pb2_grpc.PresenceStub(self.presence_channel)

        self.message_channel = grpc.aio.insecure_channel(
            f"{settings.GRPC_HOST}:{settings.GRPC_MESSAGE_PORT}"
        )
        self.message = message_pb2_grpc.MessageServiceStub(self.message_channel)

    async def stop(self):
        if self.chat_channel:
            await self.chat_channel.close()
        if self.message_channel:
            await self.message_channel.close()
        if self.presence_channel:
            await self.presence_channel.close()
        if self.user_channel:
            await self.user_channel.close()


grpc_service = GRPCService()
