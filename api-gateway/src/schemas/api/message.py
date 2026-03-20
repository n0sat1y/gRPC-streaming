from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IdBase(BaseModel):
    id: int


class UserData(IdBase):
    username: str
    avatar: str | None = None


class MessageData(BaseModel):
    id: str
    chat_id: int
    content: str
    user_id: int
    created_at: datetime


class ReactedBy(BaseModel):
    users_id: list[int] | None = None


class ReplyData(BaseModel):
    message_id: str | None = None
    user_id: int | None = None
    preview: str | None = None


class MetaData(BaseModel):
    is_edited: bool | None = None
    is_pinned: bool | None = None
    reply_to: ReplyData | None = None
    reactions: dict[str, ReactedBy] | None = None


class MessageResponseData(BaseModel):
    id: str
    chat_id: int
    user_id: int
    content: str
    created_at: datetime
    metadata: MetaData | None = None

    model_config = ConfigDict(from_attributes=True)


class GetAllMessagesSchema(BaseModel):
    messages: list[MessageResponseData]
    user_data: list[UserData]

    model_config = ConfigDict(from_attributes=True)


class GetAllMessagesResponse(BaseModel):
    count: int
    last_read_message_id: str | None
    unread_count: int
    messages: list[MessageResponseData]
    user_data: list[UserData]
