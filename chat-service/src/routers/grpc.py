from google.protobuf.json_format import MessageToDict
from loguru import logger

from protos import chat_pb2, chat_pb2_grpc
from src.services.chat import ChatService
from src.routers.kafka import broker
from src.decorators import handle_exceptions


class Chat(chat_pb2_grpc.ChatServicer):
    def __init__(self):
        self.service = ChatService()
        self.broker = broker

    @handle_exceptions
    async def GetUserChats(self, request, context):
        logger.info("Поступил запрос на получение чатов пользователя {request.id}")
        chats = await self.service.get_user_chats(request.id)
        return chat_pb2.MultipleChats(
            chats=[chat_pb2.ChatResponse(
                id=model.id, 
                name=model.name,
                avatar=model.avatar,
                last_message=model.last_message,
                last_message_at=model.last_message_at
                ) for model in chats
            ]
        )
    
    @handle_exceptions
    async def CreateChat(self, request, context):
        data = MessageToDict(request, preserving_proto_field_name=True)
        logger.info("Поступил запрос на создание чата")
        chat = await self.service.create(data, self.broker)
        return chat_pb2.ChatId(id=chat.id)
    
    @handle_exceptions
    async def GetChatData(self, request, context):
        logger.info("Поступил запрос на получение данных чата {request.id}")
        chat = await self.service.get(request.id)

        response =  chat_pb2.ChatData()
        response.id = chat.id
        response.name = chat.name
        if chat.avatar:
            response.avatar = chat.avatar
        if chat.last_message:
            response.last_message = chat.last_message
        if chat.last_message_at:
            response.last_message_at.FromDatetime(chat.last_message_at)
        response.members.extend([chat_pb2.UserId(id=member.user_id) for member in chat.members])
        response.created_at.FromDatetime(chat.created_at)

        return response
        
    @handle_exceptions
    async def UpdateChat(self, request, context):
        data = MessageToDict(request, preserving_proto_field_name=True)
        chat_id = data.pop('id')
        logger.info(f"Поступил запрос на обновление чата {chat_id}")
        chat = await self.service.update(chat_id, data)
        return chat_pb2.ChatId(id=chat.id)
    
    @handle_exceptions
    async def AddMembersToChat(self, request, context):
        data = MessageToDict(request, preserving_proto_field_name=True)
        print(data)
        chat_id = data.pop('id')
        members = data.pop('members')
        logger.info(f"Поступил запрос на добавление участников в чат {chat_id}")
        chat = await self.service.add_members(chat_id, members, self.broker)
        return chat_pb2.ChatId(id=chat.id)

    @handle_exceptions
    async def DeleteUserChat(self, request, context):
        logger.info(f"Поступил запрос на удаление пользователя {request.user_id} из чата {request.chat_id}")
        response = await self.service.delete_user_from_chat(request.user_id, request.chat_id, self.broker)
        return chat_pb2.DeleteResponse(status=response)
    
    @handle_exceptions
    async def DeleteChat(self, request, context):
        logger.info(f"Поступил запрос на удаление чата {request.id}")
        response = await self.service.delete(request.id, self.broker)
        return chat_pb2.DeleteResponse(status=response)
