from typing import Optional, List
from datetime import datetime, timezone
from beanie import Document, Indexed, Link, BackLink
from pydantic import Field

from src.models.replications import UserReplica

class Message(Document):
    chat_id: Indexed(int)
    user_id: Indexed(int)
    content: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    read_by: List[BackLink["ReadStatus"]] = Field(json_schema_extra={"original_field": "message"})

    class Settings:
        name = "messages"

class ReadStatus(Document):
    message_id: Link[Message]
    read_by: int
    read_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "read_status"

class ReadProgress(Document):
    chat_id: Indexed(int)
    user_id: Indexed(int)
    last_read_message_id: Link[Message]

    class Settings:
        name = "read_progress"
