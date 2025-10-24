import asyncio
import grpc
from loguru import logger

from protos import message_pb2_grpc, message_pb2
from src.services.message import MessageService
from src.services.chat import ChatService
from src.routers.kafka import broker
from src.decorators import handle_exceptions


class Message(message_pb2_grpc.MessageServiceServicer):
    def __init__(self):
        self.service = MessageService()
        self.chat_service = ChatService()
        self.broker = broker
    
    @handle_exceptions
    async def SendMessage(self, request, context):
        message = await self.service.insert(
            request.user_id,
            request.chat_id,
            request.content,
            request.request_id,
            request.sender_id,
            self.broker
        )
        response = message_pb2.SendMessageResponse()
        response.message_id = str(message.id)
        response.created_at.FromDatetime(message.created_at)

        return response
    
    @handle_exceptions
    async def GetAllMessages(self, request, context):
        messages, users = await self.service.get_all(request.chat_id)
        response = []
        for message in messages:
            message_obj = message_pb2.Message(
            id=str(message.id),
            chat_id=message.chat_id,
            sender=message_pb2.SenderData(
                id=message.user_id,
                username=users[message.user_id]
            ),
            content=message.content,
            is_read=message.is_read
        )
            message_obj.created_at.FromDatetime(message.created_at)
            response.append(message_obj)
        return message_pb2.AllMessages(messages=response)
    
    @handle_exceptions
    async def GetMessageData(self, request, context):
        message = await self.service.get(request.message_id, get_full=True)
        response_obj = message_pb2.FullMessageData(
            id=str(message.id),
            chat_id=message.chat_id,
            user_id=message.user_id,
            content=message.content,
            is_read=message.is_read
        )
        read_by_list = []
        for data in message.read_by:
            read_by_obj = message_pb2.ReadBy(id=data.read_by)
            read_by_obj.read_at.FromDatetime(data.read_at)
            read_by_list.append(read_by_obj)

        response_obj.created_at.FromDatetime(message.created_at)
        
        return response_obj
    
    @handle_exceptions
    async def UpdateMessage(self, request, context):
        message = await self.service.update(
            request.message_id,
            request.new_content,
            request.request_id,
            request.sender_id,
            self.broker
        )
        return message_pb2.MessageId(message_id=str(message.id))

    @handle_exceptions
    async def DeleteMessage(self, request, context):
        await self.service.delete(
            request.message_id,
            request.request_id,
            request.sender_id,
            self.broker
        )
        return message_pb2.DeleteMessageResponse(
            status='Success'
        )
    
