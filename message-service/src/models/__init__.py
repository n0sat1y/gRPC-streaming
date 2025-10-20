from typing import Optional, List
from datetime import datetime, timezone
from beanie import Document, Indexed, Link
from pydantic import Field

from src.models.replications import UserReplica

class Message(Document):
    chat_id: Indexed(int)
    user_id: Indexed(int)
    content: str
    is_readed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "messages"

class ReadStatus(Document):
    message_id: Link[Message]
    read_by: int
    read_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReadProgress(Document):
    user_id: int
    chat_id: int
    last_read_message_id: Link[Message]
