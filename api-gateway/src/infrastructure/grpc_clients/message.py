from contextlib import asynccontextmanager
from typing import Optional

import grpc
from google.protobuf.json_format import MessageToDict
from loguru import logger

from protos import message_pb2, message_pb2_grpc
from src.core.config import settings
from src.schemas.api.message import GetAllMessagesSchema
from src.utils.decorators.grpc import handle_grpc_exceptions
from src.utils.enums.grpc_enums import DirectionEnum, direction_enum_mapper


class RpcMessageService:
    def __init__(self, stub: message_pb2_grpc.MessageServiceStub):
        self.stub = stub

    @handle_grpc_exceptions
    async def send_message(
        self,
        chat_id: int,
        content: str,
        request_id: str,
        sender_id: int,
        reply_to: Optional[str] = None,
    ) -> dict:
        request = message_pb2.SendMessageRequest(
            user_id=sender_id,
            chat_id=chat_id,
            content=content,
            request_id=request_id,
            reply_to=reply_to,
        )
        response = await self.stub.SendMessage(request)

        logger.info(f"Отправлено сообщение: {response.message_id}")
        data = MessageToDict(response, preserving_proto_field_name=True)
        return data

    @handle_grpc_exceptions
    async def update_message(
        self, message_id: str, new_content: str, request_id: str, sender_id: int
    ) -> str:
        request = message_pb2.UpdateMessageRequest(
            message_id=message_id,
            new_content=new_content,
            request_id=request_id,
            sender_id=sender_id,
        )
        response = await self.stub.UpdateMessage(request)
        logger.info(f"Обновлено сообщение: {response.message_id}")
        return response.message_id

    @handle_grpc_exceptions
    async def delete_message(
        self, message_id: str, request_id: str, sender_id: int
    ) -> str:
        request = message_pb2.DeleteMessageRequest(
            message_id=message_id, request_id=request_id, sender_id=sender_id
        )
        response = await self.stub.DeleteMessage(request)
        logger.info(f"Удалено сообщение: {message_id}")
        return response.status

    @handle_grpc_exceptions
    async def get_context(
        self,
        chat_id: int,
        user_id: int,
        limit: int,
        direction: DirectionEnum,
        cursor_id: str | None = None,
    ):
        mapped_direction = direction_enum_mapper[direction]
        request = message_pb2.GetContextRequest(
            chat_id=chat_id,
            user_id=user_id,
            cursor_id=cursor_id,
            limit=limit,
            direction=mapped_direction,
        )
        print(request)
        response = await self.stub.GetContext(request)
        logger.info(f"Получено сообщений: {len(response.messages)}")
        data = MessageToDict(response, preserving_proto_field_name=True)
        # return GetAllMessagesSchema.model_validate(data)
        return data

    @handle_grpc_exceptions
    async def get_message_data(self, message_id: str):
        request = message_pb2.MessageId(message_id=message_id)
        response = await self.stub.GetMessageData(request)
        print(response)
        logger.info(f"Получено сообщение: {response.message_data.id}")
        data = MessageToDict(response, preserving_proto_field_name=True)
        return data

    @handle_grpc_exceptions
    async def add_reaction(self, message_id: str, reaction: str, author: int):
        request = message_pb2.Reaction(
            message_id=message_id, reaction=reaction, author=author
        )
        response = await self.stub.AddReaction(request)
        return None

    @handle_grpc_exceptions
    async def remove_reaction(self, message_id: str, reaction: str, author: int):
        request = message_pb2.Reaction(
            message_id=message_id, reaction=reaction, author=author
        )
        response = await self.stub.RemoveReaction(request)
        return None

    @handle_grpc_exceptions
    async def forward_messages(
        self,
        user_id: int,
        chat_id: int,
        messages: list[str],
        request_id: str,
        content: Optional[str] = None,
    ):
        request = message_pb2.ForwardMessageRequest(
            user_id=user_id,
            chat_id=chat_id,
            request_id=request_id,
            messages=messages,
            content=content,
        )
        response = await self.stub.ForwardMessage(request)
        return response
