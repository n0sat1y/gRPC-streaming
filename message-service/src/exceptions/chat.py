class ChatNotFoundError(Exception):
    def __init__(self, *args, chat_id: int):
        self.chat_id = chat_id
        super().__init__(f"Chat not found: {self.chat_id}")
