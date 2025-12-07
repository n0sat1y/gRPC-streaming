from typing import Union
from pydantic import BaseModel
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

class UpdateMessagePayload(BaseModel):
    id: str
    content: str

class MessageIdPayload(BaseModel):
    id: str

class CreatedMessageEvent(BaseModel):
    event_type: str = 'MessageCreated'
    recievers: list[int]
    data: MessageData
    request_id: str
    sender_id: int

class UpdateMessageEvent(BaseModel):
    event_type: str = 'MessageUpdated'
    recievers: list[int]
    data: UpdateMessagePayload
    request_id: str
    sender_id: int

class DeleteMessageEvent(BaseModel):
    event_type: str = 'MessageDeleted'
    recievers: list[int]
    data: MessageIdPayload
    request_id: str
    sender_id: int

class ApiGatewayReadEvent(BaseModel):
    user_id: int
    chat_id: int
    last_read_message_id: str

class SlimMessageData(BaseModel):
    id: str
    sender_id: int

class MessagesReadEvent(BaseModel):
    event_type: str = 'MessagesRead'
    data: list[SlimMessageData]
