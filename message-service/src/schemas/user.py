from typing import Literal, Optional, Union
from pydantic import BaseModel, Field

class IdSchema(BaseModel):
    id: int

class UserData(IdSchema):
    username: str
    avatar: Optional[str] = None
    is_active: bool

class UserCreatedEvent(BaseModel):
    event_type: Literal['UserCreated']
    data: UserData

class UserUpdatedEvent(BaseModel):
    event_type: Literal['UserUpdated']
    data: UserData

class UserDeactivatedEvent(BaseModel):
    event_type: Literal['UserDeactivated']
    data: IdSchema

IncomingUserEvent = Union[UserCreatedEvent, UserUpdatedEvent, UserDeactivatedEvent]
