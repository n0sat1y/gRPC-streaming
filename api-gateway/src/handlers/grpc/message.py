import grpc
from google.protobuf.json_format import MessageToDict
from loguru import logger
from protos import message_pb2, message_pb2_grpc
from contextlib import asynccontextmanager

from src.core.config import settings
from src.decorators.grpc import handle_grpc_exceptions, handle_websocket_grpc_exceptions


class RpcMessageService:
    def __init__(self):
        self.connection_url = f"{settings.GRPC_HOST}:{settings.GRPC_MESSAGE_PORT}"

    @asynccontextmanager
    async def get_stub(self):
        async with grpc.aio.insecure_channel(self.connection_url) as channel:
            stub = message_pb2_grpc.MessageServiceStub(channel)
            yield stub

    async def send_message(self, chat_id: int, content: str, request_id: str, sender_id: int) -> dict:
        async with self.get_stub() as stub:
            request = message_pb2.SendMessageRequest(
                user_id=sender_id,
                chat_id=chat_id,
                content=content,
                request_id=request_id,
                sender_id=sender_id
            )
            response = await stub.SendMessage(request)

        logger.info(f'Отправлено сообщение: {response.message_id}')
        data = MessageToDict(response, preserving_proto_field_name=True)
        return data
    
    async def update_message(self, message_id: str, new_content: str, request_id: str, sender_id: int) -> str:
        async with self.get_stub() as stub:
            request = message_pb2.UpdateMessageRequest(
                message_id=message_id,
                new_content=new_content,
                request_id=request_id,
                sender_id=sender_id
            )
            response = await stub.UpdateMessage(request)

        logger.info(f'Обновлено сообщение: {response.message_id}')
        return response.message_id
    
    async def delete_message(self, message_id: str, request_id: str, sender_id: int) -> str:
        async with self.get_stub() as stub:
            request = message_pb2.DeleteMessageRequest(
                message_id=message_id,
                request_id=request_id,
                sender_id=sender_id
            )
            response = await stub.DeleteMessage(request)

        logger.info(f'Удалено сообщение: {message_id}')
        return response.status
    
    @handle_grpc_exceptions
    async def get_all_messages(self, chat_id: int) -> dict:
        async with self.get_stub() as stub:
            request = message_pb2.GetAllMessagesRequest(
                chat_id=chat_id
            )
            response = await stub.GetAllMessages(request)

        logger.info(f'Получено сообщений: {len(response.messages)}')
        data = MessageToDict(response, preserving_proto_field_name=True)
        return data
    

    
