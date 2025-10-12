from typing import Literal, Union
from pydantic import BaseModel, model_validator

class IdSchema(BaseModel):
    id: int

class ChatData(IdSchema):
    members: list[int]

class ChatEvent(BaseModel):
    event_type: Literal['ChatCreated', 'ChatDeleted', 'ChatUpdated']
    data: Union[IdSchema, ChatData]

    @model_validator(mode='after')
    def check_data_matches_event_type(self):
        event_type = self.event_type
        data = self.data

        if event_type == 'UserCreated' or event_type == 'ChatUpdated':
            if not isinstance(data, ChatData):
                raise ValueError("Data must be Chatdata for ChatUpdated or ChatUpdated event")
            
        elif event_type == 'ChatDeleted':
            if not isinstance(data, IdSchema):
                raise ValueError("Data must be IdSchema for ChatDeleted event")
        return self
