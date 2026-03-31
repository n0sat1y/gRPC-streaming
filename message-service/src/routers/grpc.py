import asyncio
from typing import Union

import grpc
from google.protobuf import empty_pb2
from loguru import logger

from protos import message_pb2, message_pb2_grpc
from src.decorators import handle_exceptions
from src.enums.grpc_enums import DirectionEnum
from src.mappers.grpc_mapper import mapper
from src.models import Message as MessageModel
from src.routers.kafka import broker
from src.services.chat import ChatService
from src.services.message import MessageService


class Message(message_pb2_grpc.MessageServiceServicer):
    def __init__(
        self,
        chat_service: ChatService,
        message_service: MessageService,
    ):
        self.chat_service = chat_service
        self.service = message_service

    @handle_exceptions
    async def SendMessage(self, request, context):
        message = await self.service.insert(
            request.user_id,
            request.chat_id,
            request.content,
            request.request_id,
            request.reply_to,
        )
        response = mapper.send_message(message)
        return response

    @handle_exceptions
    async def GetContext(self, request, context):
        messages = await self.service.get_context(
            chat_id=request.chat_id,
            user_id=request.user_id,
            cursor_id=request.cursor_id if request.cursor_id else None,
            direction=DirectionEnum(request.direction),
            limit=request.limit,
        )
        return mapper.get_context(messages)

    @handle_exceptions
    async def GetMessageData(self, request, context):
        message = await self.service.get(request.message_id, get_full=True)
        return mapper.get_message_data(message)

    @handle_exceptions
    async def UpdateMessage(self, request, context):
        message = await self.service.update(
            request.message_id,
            request.new_content,
            request.request_id,
            request.sender_id,
        )
        return mapper.update_message(message)

    @handle_exceptions
    async def DeleteMessage(self, request, context):
        await self.service.delete(
            request.message_id, request.request_id, request.sender_id
        )
        return mapper.delete_message()

    @handle_exceptions
    async def AddReaction(self, request, context):
        await self.service.add_reaction(
            request.message_id, request.reaction, request.author
        )
        return mapper.add_reaction()

    @handle_exceptions
    async def RemoveReaction(self, request, context):
        await self.service.remove_reaction(
            request.message_id, request.reaction, request.author
        )
        return mapper.remove_reaction()

    @handle_exceptions
    async def ForwardMessage(self, request, context):
        messages = await self.service.forward_message(
            user_id=request.user_id,
            chat_id=request.chat_id,
            messages=request.messages,
            request_id=request.request_id,
            content=request.content,
        )
        response = mapper.forward_message(messages)
        return response
