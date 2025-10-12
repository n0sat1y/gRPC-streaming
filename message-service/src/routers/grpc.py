import asyncio
import grpc
from loguru import logger

from protos import message_pb2_grpc, message_pb2
from src.services.message import ConnectionService, MessageService
from src.routers.kafka import broker


class Message(message_pb2_grpc.MessageServiceServicer):
    def __init__(self):
        self.service = MessageService()
        self.manager = ConnectionService()
        self.broker = broker

    async def SubscribeMessages(self, request, context):
        try:
            chat_id = request.chat_id
            user_id = request.user_id
            self.manager.connect(chat_id, context)
            logger.info(f"Пользователь {user_id=} подключился к чату {chat_id=}")

            while True:
                await asyncio.sleep(3600)
                print(self.manager.active_connections())

        except asyncio.CancelledError:
            logger.info(f"Пользователь {user_id=} отключился от чата {chat_id=}")
            self.manager.disconnect(chat_id, context)
            raise
    
    async def SendMessage(self, request, context):
        message = await self.service.insert(
            request.user_id,
            request.chat_id,
            request.content,
            self.broker
        )

        message_obj = message_pb2.Message()
        message_obj.message_id = str(message.id)
        message_obj.chat_id = message.chat_id
        message_obj.user_id = message.user_id
        message_obj.username = ')))'
        message_obj.content = message.content
        message_obj.created_at.FromDatetime(message.created_at)

        await self.manager.broabcast(request.chat_id, message_obj)


        response = message_pb2.SendMessageResponse()
        response.status = True
        response.message_id = str(message.id)
        response.created_at.FromDatetime(message.created_at)

        return response
    
    async def GetAllMessages(self, request, context):
        messages = await self.service.get_all(request.chat_id)
        response = []
        for message in messages:
            message_obj = message_pb2.Message()
            message_obj.message_id = str(message.id)
            message_obj.chat_id = message.chat_id
            message_obj.user_id = message.user_id
            message_obj.username = ')))'
            message_obj.content = message.content
            message_obj.created_at.FromDatetime(message.created_at)
            response.append(message_obj)
        return message_pb2.AllMessages(messages=response)
    
