from typing import Literal, Union
from pydantic import BaseModel, model_validator

class IdSchema(BaseModel):
    id: int

class UserData(IdSchema):
    username: str
    is_active: bool

class UserEvent(BaseModel):
    event_type: Literal['UserCreated', 'UserDeactivated']
    data: Union[IdSchema, UserData]

    @model_validator(mode='after')
    def check_data_matches_event_type(self):
        event_type = self.event_type
        data = self.data

        if event_type == 'UserCreated':
            if not isinstance(data, UserData):
                raise ValueError("Data must be Userdata for UserCreated event")
            
        elif event_type == 'UserDeactivated':
            if not isinstance(data, IdSchema):
                raise ValueError("Data must be IdSchema for UserDeactivated event")
        return self
