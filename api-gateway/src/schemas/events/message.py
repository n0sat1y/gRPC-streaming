from datetime import datetime
from typing import Literal, Union

from pydantic import BaseModel, ConfigDict

# from src.schemas.api.message import MessageData


class UpdateMessagePayload(BaseModel):
    id: str
    content: str


class MessageIdPayload(BaseModel):
    id: str


class ReacionPayload(BaseModel):
    message_id: str
    reaction: str


class Slimdict(BaseModel):
    id: str
    sender_id: int


class CreatedMessageEvent(BaseModel):
    event_type: Literal["MessageCreated"]
    recievers: list[int]
    data: dict
    request_id: str
    sender_id: int


class CreatedManyMessagesEvent(BaseModel):
    event_type: str = "MessagesCreated"
    recievers: list[int]
    data: list[dict]
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
    data: list[Slimdict]


IncomingMessage = Union[
    CreatedMessageEvent,
    CreatedManyMessagesEvent,
    UpdateMessageEvent,
    DeleteMessageEvent,
    AddReactionEvent,
    RemoveReactionEvent,
    MessagesReadEvent,
]


class ApiGatewayReadEvent(BaseModel):
    user_id: int
    chat_id: int
    last_read_message_id: str
