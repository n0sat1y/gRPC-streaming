from typing import Optional, List, Dict
from datetime import datetime, timezone
from beanie import Document, Indexed, Link, BackLink
from pydantic import Field, BaseModel


class ReplyData(BaseModel):
    message_id: str
    user_id: int
    username: str
    preview: str

class ForwardData(BaseModel):
    from_message_id: str
    from_chat_id: int
    sender_user_id: int
    sender_username: str

class MetaData(BaseModel):
    is_edited: bool = False
    is_pinned: bool = False
    reactions: Dict[str, List[int]] = Field(default_factory=dict)
    reply_to: Optional[ReplyData] = None
    forward_from: Optional[ForwardData] = None
    url_preview: Optional[str] = None


class Message(Document):
    user_id: int
    chat_id: int
    content: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: MetaData = Field(default_factory=MetaData)

    read_by: List[BackLink["ReadStatus"]] = Field(
        default_factory=list,
        json_schema_extra={"original_field": "message_id"}
    )

    class Settings:
        name = "messages"
        indexes = [
            'chat_id', 
            'user_id',
            ('chat_id', '-created_at')
        ]

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
