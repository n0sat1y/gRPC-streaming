from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ChatMemberSchema(BaseModel):
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class GetFullChatData(BaseModel):
    name: str
    created_at: datetime
    members: list[ChatMemberSchema]

    model_config = ConfigDict(from_attributes=True)

class GetChatData(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class GetUserChats(BaseModel):
    chats: list[GetChatData]

    model_config = ConfigDict(from_attributes=True)

