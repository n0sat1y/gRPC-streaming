from datetime import datetime
from typing import Literal, Union
from pydantic import BaseModel, model_validator

class IdSchema(BaseModel):
    id: int

class MessageData(IdSchema):
    id: str
    chat_id: int
    content: str
    created_at: datetime

class MessageEvent(BaseModel):
    event_type: Literal['MessageCreated']
    data: Union[MessageData]

    @model_validator(mode='after')
    def check_data_matches_event_type(self):
        event_type = self.event_type
        data = self.data

        if event_type == 'MessageCreated':
            if not isinstance(data, MessageData):
                raise ValueError("Data must be MessageData for MessageCreated event")
        return self
