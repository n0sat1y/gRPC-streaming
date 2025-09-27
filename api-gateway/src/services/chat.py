import grpc
from loguru import logger
from google.protobuf.json_format import MessageToDict
from protos import chat_pb2, chat_pb2_grpc
from contextlib import asynccontextmanager

from src.core.config import settings
from src.decorators.grpc import handle_grpc_exceptions
from src.schemas.chat import *


class RpcChatService:
    def __init__(self):
        self.connection_url = f"{settings.GRPC_HOST}:{settings.GRPC_CHAT_PORT}"

    @asynccontextmanager
    async def get_stub(self):
        async with grpc.aio.insecure_channel(self.connection_url) as channel:
            stub = chat_pb2_grpc.ChatStub(channel)
            yield stub

    @handle_grpc_exceptions
    async def get_chat_by_id(self, chat_id: int):
        async with self.get_stub() as stub:
            request = chat_pb2.GetChatDataRequest(chat_id=chat_id)
            response = await stub.GetChatData(request)

        logger.info(f"Получен чат: {chat_id}")
        data = MessageToDict(response, preserving_proto_field_name=True)
        return ChatData.model_validate(data)
    
    @handle_grpc_exceptions
    async def create_chat(self, data: CreateChatRequest):
        async with self.get_stub() as stub:
            request = chat_pb2.CreateChatRequest(
                name=data.name,
                members=[chat_pb2.ChatMember(id=member.id) for member in data.members]
            )
            response = await stub.CreateChat(request)

        logger.info(f"Создан чат: {response.id}")
        response = MessageToDict(response, preserving_proto_field_name=True)
        return ChatResponse.model_validate(response)

    @handle_grpc_exceptions
    async def get_chats_by_user_id(self, user_id: int):
        async with self.get_stub() as stub:
            request = chat_pb2.GetUserChatsRequest(user_id=user_id)
            response = await stub.GetUserChats(request)

        logger.info(f"Получены чаты: {user_id}")
        data = MessageToDict(response, preserving_proto_field_name=True)
        return MultipleChatsResponse.model_validate(data)
    
    @handle_grpc_exceptions
    async def add_members_to_chat(self, data: AddMembersToChatRequest):
        async with self.get_stub() as stub:
            request = chat_pb2.AddMembersToChatRequest(
                chat_id=data.chat_id,
                members=[chat_pb2.ChatMember(id=member.id) for member in data.members]
            )
            response = await stub.AddMembersToChat(request)

        logger.info(f"Добавлены пользователи: {', '.join([str(member.id) for member in data.members])}")
        response = MessageToDict(response, preserving_proto_field_name=True)
        return ChatResponse.model_validate(response)

    @handle_grpc_exceptions
    async def delete_user_from_chat(self, user_id: int, chat_id: int):
        async with self.get_stub() as stub:
            request = chat_pb2.DeleteUserChatRequest(user_id=user_id, chat_id=chat_id)
            response = await stub.DeleteUserChat(request)

        logger.info(f"Пользователь {user_id=} был удален из чата {chat_id=}")
        return {'status': response.status}
    
    @handle_grpc_exceptions
    async def delete_chat(self, chat_id: int):
        async with self.get_stub() as stub:
            request = chat_pb2.DeleteChatRequest(chat_id=chat_id)
            response = await stub.DeleteChat(request)

        logger.info(f"Чат был удален {chat_id=}")
        return {'status': response.status}
