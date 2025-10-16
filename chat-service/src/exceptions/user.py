class UsersNotFoundError(Exception):
    def __init__(self, missed: list):
        self.missed = missed
        super().__init__(f"Missed users: {', '.join(str(i) for i in self.missed)}")
