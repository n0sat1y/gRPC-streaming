from typing import Literal
from pydantic import BaseModel

class UserIdSchema(BaseModel):
    id: int

class UserData(UserIdSchema):
    username: str
    avatar: str | None = None
    is_active: bool

    class Config:
        from_attributes = True

class UserCreatedEvent(BaseModel):
    event_type: Literal['UserCreated'] = 'UserCreated'
    data: UserData

class UserDeactivateEvent(BaseModel):
    event_type: Literal['UserDeactivated'] = 'UserDeactivated'
    data: UserIdSchema

class UserUpdatedEvent(BaseModel):
    event_type: Literal['UserUpdated'] = 'UserUpdated'
    data: UserData
