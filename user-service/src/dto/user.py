from dataclasses import dataclass

@dataclass
class UpdateUserDataDTO:
    id: int
    username: str | None = None
    avatar: str | None = None

