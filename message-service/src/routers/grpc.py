import asyncio
from typing import Union
import grpc
from loguru import logger
from google.protobuf import empty_pb2

from protos import message_pb2_grpc, message_pb2
from src.services.message import MessageService
from src.services.chat import ChatService
from src.routers.kafka import broker
from src.decorators import handle_exceptions
from src.models import Message as MessageModel


class Message(message_pb2_grpc.MessageServiceServicer):
    def __init__(
        self,
        chat_service: ChatService,
        message_service: MessageService
    ):
        self.chat_service = chat_service
        self.service = message_service

    def _add_metadata(
        self, 
        message: MessageModel, 
        obj: Union[message_pb2.Message, message_pb2.FullMessageData]
    ) -> Union[message_pb2.Message, message_pb2.FullMessageData]:
        reply_to_obj = message_pb2.ReplyData()
        reply_data = message.metadata.reply_to
        if reply_data:
             reply_to_obj.message_id = reply_data.message_id
             reply_to_obj.user_id = reply_data.user_id
             reply_to_obj.username = reply_data.username
             reply_to_obj.preview = reply_data.preview

        metadata_obj = message_pb2.Metadata(
            is_edited=message.metadata.is_edited,
            is_pinned=message.metadata.is_pinned,
            reply_to=reply_to_obj,
        )
        print(message.metadata.reactions)
        for reaction, reacted_by in message.metadata.reactions.items():
            reacted_by_obj = message_pb2.ReactedBy(users_id=reacted_by)
            metadata_obj.reactions[reaction].CopyFrom(reacted_by_obj)

        obj.metadata.CopyFrom(metadata_obj)
        return obj

    def _get_slim_message_obj(
        self, 
        message: MessageModel, 
        users: dict, 
        obj: message_pb2.Message,
    ) -> message_pb2.Message:
        obj.id = str(message.id)
        obj.chat_id = message.chat_id
        obj.sender.CopyFrom(
            message_pb2.SenderData(
                id=message.user_id,
                username=users[message.user_id]
            )
        )
        obj.content = message.content
        obj.is_read = message.is_read
        obj.created_at.FromDatetime(message.created_at)
        obj = self._add_metadata(message, obj)
        print(obj)
        return obj

    
    @handle_exceptions
    async def SendMessage(self, request, context):
        message = await self.service.insert(
            request.user_id,
            request.chat_id,
            request.content,
            request.request_id,
            request.sender_id,
            request.reply_to,
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
            message_obj = self._get_slim_message_obj(message, users, message_obj)
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
        response_obj.read_by.extend(read_by_list)
        response_obj.created_at.FromDatetime(message.created_at)
        response_obj = self._add_metadata(message, response_obj)
        
        return response_obj
    
    @handle_exceptions
    async def UpdateMessage(self, request, context):
        message = await self.service.update(
            request.message_id,
            request.new_content,
            request.request_id,
            request.sender_id
        )
        return message_pb2.MessageId(message_id=str(message.id))

    @handle_exceptions
    async def DeleteMessage(self, request, context):
        await self.service.delete(
            request.message_id,
            request.request_id,
            request.sender_id
        )
        return message_pb2.DeleteMessageResponse(
            status='Success'
        )
    
    @handle_exceptions
    async def AddReaction(self, request, context):
        await self.service.add_reaction(
            request.message_id,
            request.reaction,
            request.author
        )
        return empty_pb2.Empty()
    
    @handle_exceptions
    async def RemoveReaction(self, request, context):
        await self.service.remove_reaction(
            request.message_id,
            request.reaction,
            request.author
        )
        return empty_pb2.Empty()
