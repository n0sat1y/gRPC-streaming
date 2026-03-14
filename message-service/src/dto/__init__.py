from dataclasses import dataclass

from src.models import Message
from src.models.replications import UserReplica


@dataclass
class MessageDTO:
    message: Message
    users: dict[int, UserReplica] = {}


@dataclass
class ManyMessagesDTO:
    messages: list[Message] = []
    users: dict[str, UserReplica] = {}
