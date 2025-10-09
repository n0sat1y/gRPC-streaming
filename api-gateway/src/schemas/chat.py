from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class IdSchema(BaseModel):
    id: int

class ChatResponse(BaseModel):
    id: int
    name: str
    avatar: Optional[str] = None
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None

class MultipleChatsResponse(BaseModel):
    chats: list[ChatResponse]

class FullChatMember(BaseModel):
    id: int

class ChatData(BaseModel):
    id: int
    name: str
    members: list[FullChatMember]
    avatar: Optional[str] = None
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    created_at: datetime


class CreateChatRequest(BaseModel):
    name: str
    members: list[IdSchema]

class AddMembersToChatRequest(BaseModel):
    chat_id: int
    members: list[IdSchema]
