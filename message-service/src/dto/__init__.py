from dataclasses import dataclass, field

from src.models import Message
from src.models.replications import UserReplica


@dataclass
class MessageDTO:
    message: Message
    users: dict[int, UserReplica] = field(default_factory=dict)
    read_by: list[int] = field(default_factory=list)


@dataclass
class ManyMessagesDTO:
    count: int | None = None
    unread_count: int | None = None
    messages: list[Message] = field(default_factory=list)
    users: dict[int, UserReplica] = field(default_factory=dict)
    last_read_message_id: str | None = None
