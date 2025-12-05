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

class ChatMemberUpdateFailed(Exception):
    def __init__(self):
        super().__init__(f"Failed to update member")

class WrongChatType(Exception):
    def __init__(self):
        super().__init__(f"Wrong chat type recieved")

class AddMembersFailed(Exception):
    def __init__(self):
        super().__init__(f"Failed to add members to chat")

class AddMembersAborted(Exception):
    def __init__(self):
        super().__init__(f"The process of adding members to the chat has been interrupted")

class MembersAlreadyAdded(Exception):
    def __init__(self):
        super().__init__(f"Members already added to chat")

class UserChatNotFound(Exception):
    def __init__(self):
        super().__init__(f"This chat not found in user chats")

class ChatMemberNotFound(Exception):
    def __init__(self):
        super().__init__(f"User not found in chat members")
