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
    messages: list[Message] = field(default_factory=list)
    users: dict[int, UserReplica] = field(default_factory=dict)
