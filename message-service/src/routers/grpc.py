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
        print(request.tmp_message_id)
        message = await self.service.insert(
            request.user_id,
            request.chat_id,
            request.content,
            request.tmp_message_id,
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
            message_obj = message_pb2.Message()
            message_obj.message_id = str(message.id)
            message_obj.chat_id = message.chat_id
            message_obj.user_id = message.user_id
            message_obj.username = users[message.user_id]
            message_obj.content = message.content
            message_obj.created_at.FromDatetime(message.created_at)
            response.append(message_obj)
        return message_pb2.AllMessages(messages=response)
    
