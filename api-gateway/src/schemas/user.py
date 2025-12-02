from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, model_validator

class UserIdSchema(BaseModel):
    id: int

class UserData(UserIdSchema):
    username: str
    avatar: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UpdateUserDataSchema(BaseModel):
    username: Optional[str] = None
    avatar: Optional[str] = None

    @model_validator(mode='after')
    def at_least_one(self):
        if not self.username and not self.avatar:
            raise ValueError('At list one optional parameter must be provided')
        return self

