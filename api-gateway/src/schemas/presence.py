from typing import Literal
from pydantic import BaseModel

class UserStatus(BaseModel):
    status: Literal['online', 'offline']

class PresenceEvent(UserStatus):
    user_id: int
    recievers: list[int]
