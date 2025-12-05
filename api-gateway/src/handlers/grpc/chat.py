import grpc
from loguru import logger
from google.protobuf.json_format import MessageToDict
from protos import chat_pb2, chat_pb2_grpc
from contextlib import asynccontextmanager

from src.core.config import settings
from src.decorators.grpc import handle_grpc_exceptions
from src.schemas.chat import *
from protos import chat_pb2_grpc


class RpcChatService:
    def __init__(self, stub: chat_pb2_grpc.ChatStub):
        self.stub = stub

    @handle_grpc_exceptions
    async def get_chat_by_id(self, chat_id: int, user_id: int):
        request = chat_pb2.GetChatRequest(chat_id=chat_id, user_id=user_id)
        response = await self.stub.GetChatData(request)

        logger.info(f"Получен чат: {chat_id}")
        data = MessageToDict(response, preserving_proto_field_name=True)
        print(data)
        return ChatData.model_validate(data)
    
    @handle_grpc_exceptions
    async def get_or_create_private_chat(self, data: GetOrCreatePrivateChatRequest):
        print(data)
        request = chat_pb2.CreatePrivateChatRequest(
            current_user_id=data.current_user_id, 
            target_user_id=data.target_user_id
        )
        print(request)
        response = await self.stub.GetOrCreatePrivateChat(request)

        logger.info(f"Создан чат: {response.id}")
        response = MessageToDict(response, preserving_proto_field_name=True)
        return IdSchema.model_validate(response)
    
    @handle_grpc_exceptions
    async def create_group_chat(self, data: CreateGroupChatRequest):
        request = chat_pb2.CreateGroupChatRequest(
            name=data.name,
            avatar=data.avatar,
            members=[chat_pb2.UserId(id=member.id) for member in data.members]
        )
        response = await self.stub.CreateGroupChat(request)

        logger.info(f"Создан чат: {response.id}")
        response = MessageToDict(response, preserving_proto_field_name=True)
        return IdSchema.model_validate(response)

    @handle_grpc_exceptions
    async def get_chats_by_user_id(self, user_id: int): 
        request = chat_pb2.UserId(id=user_id)
        response = await self.stub.GetUserChats(request)
        logger.info(f"Получены чаты: {user_id}")
        data = MessageToDict(response, preserving_proto_field_name=True)
        print(data)
        return MultipleChatsResponse.model_validate(data)
    
    @handle_grpc_exceptions
    async def get_last_read_message(self, chat_id: int, user_id: int):
        request = chat_pb2.GetLastReadMessageRequest(chat_id=chat_id, user_id=user_id)
        response = await self.stub.GetLastReadMessage(request)
        logger.info(f"Получено сообщение: {response.message_id}")
        return response.message_id
    
    @handle_grpc_exceptions
    async def update_chat(self, data: UpdateChatData):
        request = chat_pb2.UpdateChatRequest(
            id=data.chat_id,
            name=data.name,
            avatar=data.avatar
        )
        response = await self.stub.UpdateChat(request)
        logger.info(f"Обновлен чат : {data.chat_id}")
        return IdSchema.model_validate(response)
    
    @handle_grpc_exceptions
    async def add_members(self, data: AddMembersRequest):
        request = chat_pb2.AddMembersRequest(
            id=data.id,
            members=[chat_pb2.UserId(id=member.id) for member in data.members]
        )
        response = await self.stub.AddMembersToChat(request)
        logger.info(f"Пользователи добавлены в чат: {data.id}")
        return IdSchema.model_validate(response)

    @handle_grpc_exceptions
    async def delete_user_from_chat(self, user_id: int, chat_id: int):
        request = chat_pb2.DeleteUserFromChatRequest(
            user_id=user_id, 
            chat_id=chat_id
        )
        response = await self.stub.DeleteUserChat(request)
        logger.info(f"Пользователь {user_id=} был удален из чата {chat_id=}")
        return {'status': response.status}
    
    @handle_grpc_exceptions
    async def delete_chat(self, chat_id: int):
        request = chat_pb2.ChatId(id=chat_id)
        response = await self.stub.DeleteChat(request)
        logger.info(f"Чат был удален {chat_id=}")
        return {'status': response.status}
