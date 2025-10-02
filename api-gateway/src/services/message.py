import grpc
from google.protobuf.json_format import MessageToDict
from loguru import logger
from protos import message_pb2, message_pb2_grpc
from contextlib import asynccontextmanager
from fastapi import WebSocket, WebSocketDisconnect

from src.core.config import settings
from src.decorators.grpc import handle_grpc_exceptions, handle_websocket_grpc_exceptions
from src.schemas.message import *


class RpcMessageService:
    def __init__(self):
        self.connection_url = f"{settings.GRPC_HOST}:{settings.GRPC_MESSAGE_PORT}"

    @asynccontextmanager
    async def get_stub(self):
        async with grpc.aio.insecure_channel(self.connection_url) as channel:
            stub = message_pb2_grpc.MessageServiceStub(channel)
            yield stub

    # @handle_grpc_exceptions
    async def send_message(self, user_id: int, chat_id: int, content: str) -> dict:
        async with self.get_stub() as stub:
            request = message_pb2.SendMessageRequest(
                user_id=user_id,
                chat_id=chat_id,
                content=content,
            )
            response = await stub.SendMessage(request)

        logger.info(f'Отправлено сообщение: {response.message_id}')
        data = MessageToDict(response, preserving_proto_field_name=True)
        return data
    
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
    
    @handle_websocket_grpc_exceptions
    async def wait_for_messages(self, chat_id: int, user_id: int, ws: WebSocket):
        async with self.get_stub() as stub:
            request = message_pb2.SubscribeRequest(
                chat_id=chat_id,
                user_id=user_id
            )
            stream = stub.SubscribeMessages(request)
            try:
                async for message in stream:
                    message_json = MessageToDict(message, preserving_proto_field_name=True)
                    await ws.send_json(message_json)
            except Exception as e:
                    logger.error(f"gRPC стрим {stream} закрыт: {e}")
                    await ws.close(code=1011, reason="Server error")

    async def forward_websocket_message(self, user_id: int, chat_id: int, ws: WebSocket):
        try:
            while True:
                content = await ws.receive_text()
                await self.send_message(user_id, chat_id, content)
        except WebSocketDisconnect as e:
            print(f"WebSocket для чата {chat_id} закрыт.")
    
    

    
