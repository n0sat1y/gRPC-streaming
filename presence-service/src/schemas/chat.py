from typing import Literal, Union
from pydantic import BaseModel, model_validator

class IdSchema(BaseModel):
    id: int

class ChatData(IdSchema):
    members: list[int]

class ChatCreatedOrUpdated(BaseModel):
    event_type: Literal['ChatCreated', 'ChatUpdated']
    data: ChatData

class ChatDeleted(BaseModel):
    event_type: Literal['ChatDeleted']
    data: IdSchema

ChatEvent = Union[ChatCreatedOrUpdated, ChatDeleted]
