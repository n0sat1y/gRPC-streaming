class UserNotFoundError(Exception):
    def __init__(self, user: int | str):
        self.user = user
        super().__init__(f"User not found: {self.user}")

class UserAlreadyExistsError(Exception):
    def __init__(self, user: int | str):
        self.user = user
        super().__init__(f"User already exists: {self.user}")
