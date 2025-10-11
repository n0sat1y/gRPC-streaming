import grpc
from google.protobuf.json_format import MessageToDict

from protos import chat_pb2, chat_pb2_grpc
from src.services.chat import ChatService
from src.routers.kafka import broker


class Chat(chat_pb2_grpc.ChatServicer):
    def __init__(self):
        self.service = ChatService()
        self.broker = broker

    async def GetUserChats(self, request, context):
        chats = await self.service.get_user_chats(request.id, context)
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
    
    async def CreateChat(self, request, context):
        data = MessageToDict(request, preserving_proto_field_name=True)
        chat = await self.service.create(data, context, self.broker)
        return chat_pb2.ChatId(id=chat.id)
    
    async def GetChatData(self, request, context):
        chat = await self.service.get(request.id, context)

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
        

    async def UpdateChat(self, request, context):
        data = MessageToDict(request, preserving_proto_field_name=True)
        chat_id = data.pop('id')
        chat = await self.service.update(chat_id, data, context, self.broker)
        return chat_pb2.ChatId(id=chat.id)

    async def DeleteUserChat(self, request, context):
        response = await self.service.delete_user_from_chat(request.user_id, request.chat_id, context, self.broker)
        return chat_pb2.DeleteResponse(status=response)
    
    async def DeleteChat(self, request, context):
        response = await self.service.delete(request.id, context, self.broker)
        return chat_pb2.DeleteResponse(status=response)
