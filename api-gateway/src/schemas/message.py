from typing import Literal, Union
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class IdBase(BaseModel):
    id: int

class UserData(IdBase):
    username: str

class MessageData(BaseModel):
    id: str
    chat_id: int
    content: str
    sender: UserData
    created_at: datetime

class MessageResponseData(BaseModel):
    id: str
    chat_id: int
    user_id: int
    username: str
    content: str
    is_read: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GetAllMessagesSchema(BaseModel):
    messages: list[MessageResponseData]

    model_config = ConfigDict(from_attributes=True)

class UpdateMessagePayload(BaseModel):
    id: str
    content: str

class MessageIdPayload(BaseModel):
    id: str

class CreatedMessageEvent(BaseModel):
    event_type: Literal['MessageCreated']
    recievers: list[int]
    data: MessageData
    request_id: str
    event_id: str
    sender_id: int

class UpdateMessageEvent(BaseModel):
    event_type: Literal['MessageUpdated']
    recievers: list[int]
    data: UpdateMessagePayload
    request_id: str
    event_id: str
    sender_id: int

class DeleteMessageEvent(BaseModel):
    event_type: Literal['MessageDeleted']
    recievers: list[int]
    data: MessageIdPayload
    request_id: str
    event_id: str
    sender_id: int

IncomingMessage = Union[CreatedMessageEvent, UpdateMessageEvent, DeleteMessageEvent]
