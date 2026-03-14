from src.exceptions import AccessDeniedError
from src.models import Message
from src.models.replications import ChatReplica, UserReplica


class AccessPolicy:
    def can_modify(self, user_id: int, message: Message):
        if not user_id == message.user_id:
            raise AccessDeniedError()

    def can_see_chat(self, user_id: int, chat: ChatReplica):
        if not user_id in chat.members:
            raise AccessDeniedError()
