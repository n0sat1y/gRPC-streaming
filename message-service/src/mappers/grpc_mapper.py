from typing import Union

from google.protobuf import empty_pb2

from protos import message_pb2, message_pb2_grpc
from src.dto import ManyMessagesDTO, MessageDTO
from src.models.replications import UserReplica


class GrpcMapper:
    @classmethod
    def _add_metadata(
        cls,
        message_data: MessageDTO,
        obj: Union[message_pb2.Message, message_pb2.FullMessageData],
    ) -> Union[message_pb2.Message, message_pb2.FullMessageData]:
        reply_to_obj = message_pb2.ReplyData()
        forward_from_obj = message_pb2.ForwardData()
        message = message_data.message
        reply_data = message.metadata.reply_to
        forward_data = message.metadata.forward_from
        if reply_data:
            reply_to_obj.message_id = reply_data.message_id
            reply_to_obj.user_id = reply_data.user_id
            reply_to_obj.preview = reply_data.preview

        if forward_data:
            forward_from_obj.from_message_id = forward_data.from_message_id
            forward_from_obj.from_chat_id = forward_data.from_chat_id
            forward_from_obj.sender_user_id = forward_data.sender_user_id
        metadata_obj = message_pb2.Metadata(
            is_edited=message.metadata.is_edited,
            is_pinned=message.metadata.is_pinned,
            reply_to=reply_to_obj,
            forward_from=forward_from_obj,
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
        obj.id = str(message.id)
        obj.chat_id = message.chat_id
        obj.user_id = message.user_id
        obj.content = message.content
        obj.created_at.FromDatetime(message.created_at)
        if message.metadata:
            obj = cls._add_metadata(message_data, obj)
        return obj

    @classmethod
    def _add_user_data(
        cls,
        users_data: dict[int, UserReplica],
        obj: Union[message_pb2.ContextResponse, message_pb2.FullMessageResponse],
    ) -> Union[message_pb2.ContextResponse, message_pb2.FullMessageResponse]:
        users_list = []
        for user_data in users_data.values():
            user_obj = message_pb2.UserData(
                id=user_data.user_id,
                username=user_data.username,
                avatar=None,
            )
            users_list.append(user_obj)
        obj.user_data.extend(users_list)
        return obj

    @classmethod
    def send_message(cls, message: MessageDTO) -> message_pb2.SendMessageResponse:
        response = message_pb2.SendMessageResponse()
        response.message_id = str(message.message.id)
        response.created_at.FromDatetime(message.message.created_at)
        return response

    @classmethod
    def get_context(cls, messages: ManyMessagesDTO) -> message_pb2.ContextResponse:
        messages_obj = []
        for message in messages.messages:
            message_data = MessageDTO(message=message)
            message_obj = message_pb2.Message()
            message_obj = cls._get_slim_message_obj(
                message_data=message_data, obj=message_obj
            )
            messages_obj.append(message_obj)
        response_obj = message_pb2.ContextResponse(messages=messages_obj)
        response_obj = cls._add_user_data(messages.users, response_obj)
        response_obj.count = len(messages.messages)
        response_obj.unread_count = messages.unread_count
        response_obj.last_read_message_id = messages.last_read_message_id
        return response_obj

    @classmethod
    def get_message_data(cls, message_data: MessageDTO) -> message_pb2.FullMessageData:
        message = message_data.message
        users_data = message_data.users
        message_obj = message_pb2.FullMessageData(
            id=str(message.id),
            chat_id=message.chat_id,
            user_id=message.user_id,
            content=message.content,
            read_by=message_data.read_by,
        )
        message_obj.created_at.FromDatetime(message.created_at)
        if message.metadata:
            response_obj = cls._add_metadata(message_data, message_obj)
        response_obj = message_pb2.FullMessageResponse(message_data=message_obj)
        response_obj = cls._add_user_data(users_data, response_obj)
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

    @classmethod
    def forward_message(
        cls, messages: ManyMessagesDTO
    ) -> message_pb2.ForwardMessageResponse:
        response = message_pb2.ForwardMessageResponse()
        response_lst = []
        for message_data in messages.messages:
            message = message_pb2.SendMessageResponse()
            message.message_id = str(message_data.id)
            message.created_at.FromDatetime(message_data.created_at)
            response_lst.append(message)
        response.messages.extend(response_lst)
        return response


mapper = GrpcMapper


from src.exceptions.chat import *
from src.exceptions.message import *
