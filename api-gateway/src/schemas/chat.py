from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class IdSchema(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)

class ChatResponse(BaseModel):
    id: int
    name: str
    avatar: Optional[str] = None
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class MultipleChatsResponse(BaseModel):
    chats: list[ChatResponse]

    model_config = ConfigDict(from_attributes=True)


class ChatData(BaseModel):
    id: int
    name: str
    avatar: Optional[str] = None
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    members: list[IdSchema] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreateChatRequest(BaseModel):
    name: str
    members: list[IdSchema]

    model_config = ConfigDict(from_attributes=True)

class AddMembersToChatRequest(BaseModel):
    chat_id: int
    members: list[IdSchema]

    model_config = ConfigDict(from_attributes=True)
