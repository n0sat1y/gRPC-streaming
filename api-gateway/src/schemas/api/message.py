from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
    sender: UserData
    content: str
    is_read: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GetAllMessagesSchema(BaseModel):
    messages: list[MessageResponseData]

    model_config = ConfigDict(from_attributes=True)


class GetAllMessagesResponse(BaseModel):
    count: int
    last_read_message_id: str | None
    unread_count: int
    messages: list[MessageResponseData]
