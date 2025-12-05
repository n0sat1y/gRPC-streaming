import grpc
from google.protobuf.json_format import MessageToDict
from loguru import logger
from protos import message_pb2, message_pb2_grpc
from contextlib import asynccontextmanager

from src.core.config import settings
from src.decorators.grpc import handle_grpc_exceptions, handle_websocket_grpc_exceptions
from src.schemas.message import GetAllMessagesSchema
from protos import message_pb2_grpc

class RpcMessageService:
    def __init__(self, stub: message_pb2_grpc.MessageServiceStub):
        self.stub = stub

    async def send_message(self, chat_id: int, content: str, request_id: str, sender_id: int) -> dict:
        request = message_pb2.SendMessageRequest(
            user_id=sender_id,
            chat_id=chat_id,
            content=content,
            request_id=request_id,
            sender_id=sender_id
        )
        response = await self.stub.SendMessage(request)

        logger.info(f'Отправлено сообщение: {response.message_id}')
        data = MessageToDict(response, preserving_proto_field_name=True)
        return data
    
    async def update_message(self, message_id: str, new_content: str, request_id: str, sender_id: int) -> str:
        request = message_pb2.UpdateMessageRequest(
            message_id=message_id,
            new_content=new_content,
            request_id=request_id,
            sender_id=sender_id
        )
        response = await self.stub.UpdateMessage(request)
        logger.info(f'Обновлено сообщение: {response.message_id}')
        return response.message_id
    
    async def delete_message(self, message_id: str, request_id: str, sender_id: int) -> str:
        request = message_pb2.DeleteMessageRequest(
            message_id=message_id,
            request_id=request_id,
            sender_id=sender_id
        )
        response = await self.stub.DeleteMessage(request)
        logger.info(f'Удалено сообщение: {message_id}')
        return response.status
    
    @handle_grpc_exceptions
    async def get_all_messages(self, chat_id: int) -> GetAllMessagesSchema:
        request = message_pb2.GetAllMessagesRequest(
            chat_id=chat_id
        )
        response = await self.stub.GetAllMessages(request)
        logger.info(f'Получено сообщений: {len(response.messages)}')
        data = MessageToDict(response, preserving_proto_field_name=True)
        # return GetAllMessagesSchema.model_validate(data)
        return data
    
    @handle_grpc_exceptions
    async def get_message_data(self, message_id: str):
        request = message_pb2.MessageId(
            message_id=message_id
        )
        response = await self.stub.GetMessageData(request)
        logger.info(f'Получено сообщений: {len(response.messages)}')
        data = MessageToDict(response, preserving_proto_field_name=True)
        return data
    
