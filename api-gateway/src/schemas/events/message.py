from datetime import datetime
from typing import Literal, Union

from pydantic import BaseModel, ConfigDict

from src.schemas.api.message import MessageData


class UpdateMessagePayload(BaseModel):
    id: str
    content: str


class MessageIdPayload(BaseModel):
    id: str


class ReacionPayload(MessageIdPayload):
    reaction: str


class SlimMessageData(BaseModel):
    id: str
    sender_id: int


class CreatedMessageEvent(BaseModel):
    event_type: Literal["MessageCreated"]
    recievers: list[int]
    data: MessageData
    request_id: str
    sender_id: int


class UpdateMessageEvent(BaseModel):
    event_type: Literal["MessageUpdated"]
    recievers: list[int]
    data: UpdateMessagePayload
    request_id: str
    sender_id: int


class DeleteMessageEvent(BaseModel):
    event_type: Literal["MessageDeleted"]
    recievers: list[int]
    data: MessageIdPayload
    request_id: str
    sender_id: int


class AddReactionEvent(BaseModel):
    event_type: Literal["ReactionAdded"]
    recievers: list[int]
    data: ReacionPayload
    sender_id: int


class RemoveReactionEvent(BaseModel):
    event_type: Literal["ReactionRemoved"]
    recievers: list[int]
    data: ReacionPayload
    sender_id: int


class MessagesReadEvent(BaseModel):
    event_type: Literal["MessagesRead"]
    data: list[SlimMessageData]


IncomingMessage = Union[
    CreatedMessageEvent,
    UpdateMessageEvent,
    DeleteMessageEvent,
    AddReactionEvent,
    RemoveReactionEvent,
]


class ApiGatewayReadEvent(BaseModel):
    user_id: int
    chat_id: int
    last_read_message_id: str
