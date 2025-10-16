from pydantic import BaseModel
from datetime import datetime

class IdBase(BaseModel):
    id: int

class UserData(IdBase):
    username: str

class MessageData(BaseModel):
    id: str
    chat_id: int
    content: str
    sender: UserData
    tmp_message_id: str
    created_at: datetime

class CreatedMessageEvent(BaseModel):
    event_type: str = 'MessageCreated'
    recievers: list[int]
    data: MessageData
