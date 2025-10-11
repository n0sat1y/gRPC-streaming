from datetime import datetime
from typing import Optional, Self
from pydantic import BaseModel, ConfigDict, model_validator

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

class UpdateChatData(BaseModel):
    chat_id: int
    name: Optional[str] = None
    members: Optional[list[IdSchema]] = None
    avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def ensure_one_field_is_set(self) -> Self:
        if not self.name and not self.avatar and not self.members:
            raise ValueError("At least one value must be provided")
        return self
