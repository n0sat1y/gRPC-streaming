from typing import Union

from google.protobuf import empty_pb2
from loguru import logger

from protos import message_pb2, message_pb2_grpc
from src.dto import ManyMessagesDTO, MessageDTO


class GrpcMapper:
    @classmethod
    def _add_metadata(
        cls,
        message_data: MessageDTO,
        obj: Union[message_pb2.Message, message_pb2.FullMessageData],
    ) -> Union[message_pb2.Message, message_pb2.FullMessageData]:
        reply_to_obj = message_pb2.ReplyData()
        message = message_data.message
        users = message_data.users
        reply_data = message.metadata.reply_to
        if reply_data:
            reply_to_obj.message_id = reply_data.message_id
            reply_to_obj.user_id = reply_data.user_id
            reply_to_obj.username = users[reply_data.user_id].username
            reply_to_obj.preview = reply_data.preview

        metadata_obj = message_pb2.Metadata(
            is_edited=message.metadata.is_edited,
            is_pinned=message.metadata.is_pinned,
            reply_to=reply_to_obj,
        )
        for reaction, reacted_by in message.metadata.reactions.items():
            reacted_by_obj = message_pb2.ReactedBy(users_id=reacted_by)
            metadata_obj.reactions[reaction].CopyFrom(reacted_by_obj)

        obj.metadata.CopyFrom(metadata_obj)
        return obj

    @classmethod
    def _get_slim_message_obj(
        cls,
        message_data: MessageDTO,
        obj: message_pb2.Message,
    ) -> message_pb2.Message:
        message = message_data.message
        users = message_data.users
        obj.id = str(message.id)
        obj.chat_id = message.chat_id
        obj.sender.CopyFrom(
            message_pb2.SenderData(
                id=message.user_id, username=users[message.user_id].username
            )
        )
        obj.content = message.content
        obj.is_read = message.is_read
        obj.created_at.FromDatetime(message.created_at)
        if message.metadata:
            obj = self._add_metadata(message_data, obj)
        print(obj)
        return obj

    @classmethod
    def send_message(cls, message: MessageDTO) -> message_pb2.SendMessageResponse:
        response = message_pb2.SendMessageResponse()
        response.message_id = str(message.message.id)
        response.created_at.FromDatetime(message.message.created_at)
        return response

    @classmethod
    def get_all(cls, messages: ManyMessagesDTO) -> message_pb2.AllMessages:
        response = []
        for message in messages:
            message_obj = message_pb2.Message()
            message_obj = cls._get_slim_message_obj(
                message_data=message, obj=message_obj
            )
            response.append(message_obj)
        return message_pb2.AllMessages(messages=response)

    @classmethod
    def get_message_data(cls, message_data: MessageDTO) -> message_pb2.FullMessageData:
        message = message_data.message
        response_obj = message_pb2.FullMessageData(
            id=str(message.id),
            chat_id=message.chat_id,
            user_id=message.user_id,
            content=message.content,
            is_read=message.is_read,
        )
        read_by_list = []
        for data in message.read_by:
            read_by_obj = message_pb2.ReadBy(id=data.read_by)
            read_by_obj.read_at.FromDatetime(data.read_at)
            read_by_list.append(read_by_obj)
        response_obj.read_by.extend(read_by_list)
        response_obj.created_at.FromDatetime(message.created_at)
        if message.metadata:
            response_obj = cls._add_metadata(message_data, response_obj)
        return response_obj

    @classmethod
    def update_message(cls, message: MessageDTO) -> message_pb2.MessageId:
        return message_pb2.MessageId(message_id=str(message.message.id))

    @classmethod
    def delete_message(cls) -> message_pb2.DeleteMessageResponse:
        return message_pb2.DeleteMessageResponse(status="Success")

    @classmethod
    def add_reaction(cls) -> empty_pb2.Empty:
        return empty_pb2.Empty()

    @classmethod
    def remove_reaction(cls) -> empty_pb2.Empty:
        return empty_pb2.Empty()


mapper = GrpcMapper

