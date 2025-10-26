from typing import Literal
from pydantic import BaseModel

class PresenceEvent(BaseModel):
    user_id: int
    status: Literal['online', 'offline']
    recievers: list[int]

class UserStatus(BaseModel):
    status: str
