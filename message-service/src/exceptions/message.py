class DataLossError(Exception):
    def __init__(self, *args, err):
        self.err = err
        super().__init__(f"Wrong data: {self.err}")
