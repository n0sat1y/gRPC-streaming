from datetime import datetime, timezone
from beanie import Document, Indexed
from pydantic import Field

class Message(Document):
    chat_id: Indexed(int)
    user_id: Indexed(int)
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "messages"


