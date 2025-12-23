class DataLossError(Exception):
    def __init__(self, *args, err):
        self.err = err
        super().__init__(f"Wrong data: {self.err}")

class MessageNotFoundError(Exception):
    def __init__(self, *args, message_id: str):
        self.message_id = message_id
        super().__init__(f"Message not found: {self.message_id}")

class ReacionNotAdded(Exception):
    def __init__(self, *args):
        super().__init__(f"Reaction already added")
