class UserNotFoundError(Exception):
    def __init__(self, *args, user_id: int):
        self.user_id = user_id
        super().__init__(f"User not found: {user_id}")
