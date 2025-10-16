class ChatNotFoundError(Exception):
    def __init__(self, chat: int | str):
        self.chat = chat
        super().__init__(f"Chat not found: {self.chat}")

class ChatAlreadyExistsError(Exception):
    def __init__(self, chat: int | str):
        self.chat = chat
        super().__init__(f"Chat already exists: {self.chat}")

class ChatUpdateFailed(Exception):
    def __init__(self):
        super().__init__(f"Failed to update chat")

class AddMembersFailed(Exception):
    def __init__(self):
        super().__init__(f"Failed to add members to chat")

class MembersAlreadyAdded(Exception):
    def __init__(self):
        super().__init__(f"Members already added to chat")

class UserChatNotFound(Exception):
    def __init__(self):
        super().__init__(f"This chat not found in user chats")
