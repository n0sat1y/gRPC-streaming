from src.exceptions import NotFoundError


class ChatNotFoundError(NotFoundError):
    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        super().__init__(f"Chat not found: {self.chat_id}")
