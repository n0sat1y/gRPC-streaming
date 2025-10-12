from beanie import Document, Indexed
from pydantic import Field

class UserReplica(Document):
    user_id: int = Field(..., unique=True)
    username: str
    is_active: bool

    class Settings:
        name = "users_replica"

class ChatReplica(Document):
    chat_id: int = Field(..., unique=True)
    members: list[int] = []

    class Settings:
        name = "chats_replica"
