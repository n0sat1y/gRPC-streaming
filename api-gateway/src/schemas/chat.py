from datetime import datetime
from typing import Optional, Self
from pydantic import BaseModel, ConfigDict, model_validator

class IdSchema(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)

class ChatResponse(BaseModel):
    id: int
    type: str
    title: str
    avatar: Optional[str] = None
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    interlocutor_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class MultipleChatsResponse(BaseModel):
    chats: list[ChatResponse]

    model_config = ConfigDict(from_attributes=True)


class ChatData(BaseModel):
    id: int
    type: str
    title: str
    avatar: Optional[str] = None
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    members: list[IdSchema] = []
    created_at: datetime
    interlocutor_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class CreateGroupChatRequest(BaseModel):
    name: str
    avatar: Optional[str] = None
    members: list[IdSchema]

    model_config = ConfigDict(from_attributes=True)

class GetOrCreatePrivateChatRequest(BaseModel):
    current_user_id: int
    target_user_id: int

class UpdateChatData(BaseModel):
    chat_id: int
    name: Optional[str] = None
    avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def ensure_one_field_is_set(self) -> Self:
        if not self.name and not self.avatar:
            raise ValueError("At least one value must be provided")
        return self
    
class AddMembersRequest(IdSchema):
    members: Optional[list[IdSchema]] = None

    model_config = ConfigDict(from_attributes=True)

class MessageIdSchema(IdSchema):
    message_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
