from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class ChatMemberBase(BaseModel):
    """Базовая схема для участника чата."""
    user_id: int


class ChatMemberCreate(ChatMemberBase):
    """Схема для добавления нового участника в чат."""
    pass


class ChatMember(ChatMemberBase):
    """Схема для отображения участника чата (ответ от API)."""
    id: int
    chat_id: int
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatBase(BaseModel):
    """Базовая схема чата с основными полями."""
    name: str
    avatar: Optional[str] = None


class ChatCreate(ChatBase):
    """Схема для создания нового чата."""
    members: List[ChatMemberCreate]


class ChatUpdate(BaseModel):
    """Схема для обновления информации о чате. Все поля опциональны."""
    name: Optional[str] = None
    avatar: Optional[str] = None


class Chat(ChatBase):
    """Основная схема чата для ответа от API. Включает все поля и вложенных участников."""
    id: int
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    created_at: datetime

    members: List[ChatMember] = []

    model_config = ConfigDict(from_attributes=True)
